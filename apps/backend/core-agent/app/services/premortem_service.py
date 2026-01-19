"""Premortem service for risk assessment."""

from typing import List, Optional
from sqlalchemy.orm import Session

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import Commitment, PremortermRisk
from shared.schemas import AgentDecision, Signals
from shared.observability import get_logger, trace_function

logger = get_logger(__name__)


PREMORTEM_SYSTEM_PROMPT = """You are an AI learning coach helping users identify potential obstacles to their learning goals.
Your job is to:
1. Take their stated failure reasons seriously
2. Identify specific, actionable mitigations for each risk
3. Prioritize risks by likelihood and impact
4. Be realistic but not discouraging

Focus on practical, concrete mitigations that the user can actually implement."""


PREMORTEM_PROMPT_TEMPLATE = """The user's goal is: {goal}
Timeline: {weeks_remaining} weeks
Weekly hours: {weekly_hours}

The user identified these potential reasons they might fail:
{failure_reasons}

For each risk, provide:
1. A specific mitigation strategy
2. A priority (1-5, where 1 is highest priority)

Respond in JSON format:
{{
    "risks": [
        {{
            "risk": "Original risk statement",
            "mitigation": "Specific mitigation strategy",
            "priority": 1
        }}
    ],
    "summary": "Brief summary of risk mitigation plan",
    "key_insight": "Most important insight about their risks"
}}"""


class PremortermService:
    """Service for premortem risk assessment."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    @trace_function(name="process_premortem", tags=["premortem", "core-agent"])
    async def process_premortem(
        self,
        user_id: int,
        failure_reasons: List[str],
    ) -> AgentDecision:
        """Process premortem assessment and generate mitigations.
        
        Args:
            user_id: User ID
            failure_reasons: List of potential failure reasons
            
        Returns:
            AgentDecision with risks and mitigations
        """
        logger.info("Processing premortem", user_id=user_id, num_risks=len(failure_reasons))
        
        # Get active commitment
        commitment = self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).first()
        
        if not commitment:
            return AgentDecision(
                reason="No active commitment found. Please complete intake first.",
                signals=Signals(adherence=0.0, knowledge=0.0, retention=0.0, status="at_risk"),
                action={"plan_adjustment": "keep", "risk_mitigation": []},
                next_tasks=[{"task": "Complete intake assessment", "timebox_min": 10, "type": "review"}],
                resources_used=[],
                quality_score=1.0,
                quality_flags=["no_commitment"],
            )
        
        # Calculate weeks remaining
        from datetime import date
        weeks_remaining = (commitment.target_date - date.today()).days // 7
        
        # Format failure reasons as numbered list
        reasons_text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(failure_reasons[:5]))
        
        # Get LLM analysis
        try:
            prompt = PREMORTEM_PROMPT_TEMPLATE.format(
                goal=commitment.goal,
                weeks_remaining=max(1, weeks_remaining),
                weekly_hours=commitment.weekly_hours,
                failure_reasons=reasons_text,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "risks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "risk": {"type": "string"},
                                    "mitigation": {"type": "string"},
                                    "priority": {"type": "integer"},
                                },
                            },
                        },
                        "summary": {"type": "string"},
                        "key_insight": {"type": "string"},
                    },
                    "required": ["risks", "summary"],
                },
                system_prompt=PREMORTEM_SYSTEM_PROMPT,
            )
            
            risks = llm_response.get("risks", [])
            summary = llm_response.get("summary", "Risk assessment complete")
            
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            # Fallback: create simple mitigations
            risks = [
                {"risk": r, "mitigation": "Create accountability checkpoint", "priority": i+1}
                for i, r in enumerate(failure_reasons[:5])
            ]
            summary = "Risk assessment complete. Consider these mitigations."
        
        # Clear existing risks and save new ones
        self.db.query(PremortermRisk).filter(
            PremortermRisk.commitment_id == commitment.id
        ).delete()
        
        for risk_data in risks:
            risk = PremortermRisk(
                commitment_id=commitment.id,
                risk=risk_data.get("risk", ""),
                mitigation=risk_data.get("mitigation", ""),
                priority=risk_data.get("priority", 5),
            )
            self.db.add(risk)
        
        self.db.commit()
        
        # Build mitigation rules for response
        mitigation_rules = [r.get("mitigation", "")[:50] for r in risks[:3]]
        
        return AgentDecision(
            reason=summary,
            signals=Signals(
                adherence=1.0,
                knowledge=0.0,
                retention=0.0,
                status="active",
            ),
            action={
                "plan_adjustment": "keep",
                "risk_mitigation": mitigation_rules,
            },
            next_tasks=[
                {"task": "Review your weekly learning plan", "timebox_min": 20, "type": "reading"},
                {"task": f"Start with: {commitment.goal.split()[0] if commitment.goal else 'basics'}", "timebox_min": 45, "type": "reading"},
            ],
            resources_used=[],
            quality_score=1.0,
            quality_flags=[],
        )
    
    def get_risks(self, commitment_id: int) -> List[PremortermRisk]:
        """Get all risks for a commitment."""
        return self.db.query(PremortermRisk).filter(
            PremortermRisk.commitment_id == commitment_id
        ).order_by(PremortermRisk.priority).all()
