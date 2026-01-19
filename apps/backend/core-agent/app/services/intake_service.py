"""Intake service for commitment contract creation."""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import User, Commitment, LearningStyle
from shared.schemas import AgentDecision, Signals, NextTask
from shared.observability import get_logger, trace_function

logger = get_logger(__name__)


INTAKE_SYSTEM_PROMPT = """You are an AI learning coach helping users create a commitment contract for their learning goal.
Your job is to:
1. Acknowledge their goal and timeline
2. Assess if the timeline is realistic given their available hours
3. Suggest an initial learning approach based on their style
4. Provide encouraging but realistic feedback

Always be supportive but honest about what's achievable."""


INTAKE_PROMPT_TEMPLATE = """User wants to learn:
Goal: {goal}
Target Date: {target_date}
Weekly Hours Available: {weekly_hours}
Background: {background}
Current Level: {baseline_level}
Learning Style Preference: {learning_style}

Create a personalized response that:
1. Validates their goal
2. Estimates if the timeline is achievable
3. Suggests the best approach for their learning style
4. Provides 1-2 initial recommended actions

Respond in JSON format:
{{
    "reason": "Your analysis of their goal and approach",
    "timeline_assessment": "realistic|ambitious|conservative",
    "recommended_approach": "Description of suggested learning path",
    "initial_tasks": ["Task 1", "Task 2"]
}}"""


class IntakeService:
    """Service for handling user intake and commitment creation."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    @trace_function(name="create_commitment", tags=["intake", "core-agent"])
    async def create_commitment(
        self,
        user_id: int,
        goal: str,
        target_date: date,
        weekly_hours: int,
        background: Optional[str] = None,
        baseline_level: Optional[str] = None,
        learning_style: str = "mixed",
    ) -> AgentDecision:
        """Create a new learning commitment contract.
        
        Args:
            user_id: User ID
            goal: Learning goal
            target_date: Target completion date
            weekly_hours: Available hours per week
            background: Student or professional
            baseline_level: Beginner, intermediate, advanced
            learning_style: Reading, coding, or mixed
            
        Returns:
            AgentDecision with commitment details and first steps
        """
        logger.info("Creating commitment", user_id=user_id, goal=goal[:50])
        
        # Deactivate any existing active commitments
        self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).update({"is_active": False})
        
        # Create new commitment
        style_enum = LearningStyle(learning_style) if learning_style in [e.value for e in LearningStyle] else LearningStyle.MIXED
        
        commitment = Commitment(
            user_id=user_id,
            goal=goal,
            target_date=target_date,
            weekly_hours=weekly_hours,
            background=background,
            baseline_level=baseline_level,
            learning_style=style_enum,
            is_active=True,
        )
        
        self.db.add(commitment)
        self.db.commit()
        self.db.refresh(commitment)
        
        # Get LLM analysis
        try:
            prompt = INTAKE_PROMPT_TEMPLATE.format(
                goal=goal,
                target_date=target_date,
                weekly_hours=weekly_hours,
                background=background or "Not specified",
                baseline_level=baseline_level or "Not specified",
                learning_style=learning_style,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"},
                        "timeline_assessment": {"type": "string"},
                        "recommended_approach": {"type": "string"},
                        "initial_tasks": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["reason", "timeline_assessment", "initial_tasks"],
                },
                system_prompt=INTAKE_SYSTEM_PROMPT,
            )
            
            reason = llm_response.get("reason", "Commitment created successfully")
            initial_tasks = llm_response.get("initial_tasks", ["Complete premortem assessment"])
            
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            reason = "Commitment created successfully. Let's start with a premortem assessment."
            initial_tasks = ["Complete premortem assessment"]
        
        # Build response
        next_tasks = [
            NextTask(
                task=initial_tasks[0] if initial_tasks else "Complete premortem assessment",
                timebox_min=15,
                type="review",
                priority=1,
            )
        ]
        
        if len(initial_tasks) > 1:
            next_tasks.append(
                NextTask(
                    task=initial_tasks[1],
                    timebox_min=20,
                    type="reading",
                    priority=2,
                )
            )
        
        return AgentDecision(
            reason=reason,
            signals=Signals(
                adherence=1.0,
                knowledge=0.0,
                retention=0.0,
                status="active",
            ),
            action={"plan_adjustment": "keep", "risk_mitigation": []},
            next_tasks=[t.model_dump() for t in next_tasks],
            resources_used=[],
            quality_score=1.0,
            quality_flags=[],
        )
    
    def get_active_commitment(self, user_id: int) -> Optional[Commitment]:
        """Get user's active commitment."""
        return self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).first()
