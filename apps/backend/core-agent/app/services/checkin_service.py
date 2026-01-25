"""Check-in service for daily standups."""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
import httpx

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import Checkin, Plan, DailyTask, MemoryRule, UserStatus, TaskStatus
from shared.schemas import AgentDecision, Signals
from shared.observability import get_logger, trace_function
from app.core.config import settings

logger = get_logger(__name__)


CHECKIN_SYSTEM_PROMPT = """You are an AI learning coach processing a daily check-in.
Your job is to:
1. Acknowledge what they accomplished yesterday
2. Help them plan for today based on their current state
3. If they have blockers, provide specific guidance
4. Suggest fallback mini-tasks if they're struggling

Be encouraging but honest. Focus on momentum over perfection."""


CHECKIN_PROMPT_TEMPLATE = """User's daily check-in:
Yesterday: {yesterday}
Today's plan: {today}
Blockers: {blockers}

Current plan tasks for today:
{today_tasks}

Their goal: {goal}
Status: Week {current_week}, {weeks_remaining} weeks remaining
Recent patterns: {patterns}

Provide:
1. Your assessment of their progress
2. Recommended next task (specific and achievable)
3. A fallback mini-task (15-20 min) if they're struggling
4. If blocker present, specific advice on overcoming it

Respond in JSON format:
{{
    "assessment": "Your assessment of their check-in",
    "next_task": "The best next action to take",
    "next_task_timebox": 45,
    "fallback_task": "A smaller fallback if struggling",
    "blocker_advice": "Specific advice if blocker present (null if no blocker)",
    "motivation_note": "Brief encouraging note"
}}"""


class CheckinService:
    """Service for daily standup check-ins."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    @trace_function(name="process_checkin", tags=["checkin", "core-agent"])
    async def process_checkin(
        self,
        user_id: int,
        yesterday: Optional[str] = None,
        today: Optional[str] = None,
        blockers: Optional[str] = None,
    ) -> AgentDecision:
        """Process daily check-in and provide guidance.
        
        Args:
            user_id: User ID
            yesterday: What they did yesterday
            today: What they plan today
            blockers: Any blockers
            
        Returns:
            AgentDecision with next steps and guidance
        """
        logger.info("Processing check-in", user_id=user_id, has_blocker=bool(blockers))
        
        # Get active plan and commitment
        from shared.db.models import Commitment
        
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
        
        # Calculate progress
        weeks_remaining = max(1, (commitment.target_date - date.today()).days // 7)
        current_week = max(1, (date.today() - commitment.created_at.date()).days // 7 + 1)
        
        # Get today's tasks
        plan = self.db.query(Plan).filter(
            Plan.user_id == user_id,
            Plan.is_active == True
        ).first()
        
        today_tasks = []
        if plan:
            tasks = self.db.query(DailyTask).filter(
                DailyTask.plan_id == plan.id,
                DailyTask.date == date.today()
            ).all()
            today_tasks = [f"- {t.task} ({t.timebox_min}min)" for t in tasks]
        
        # Get memory rules (patterns)
        memory_rules = self.db.query(MemoryRule).filter(
            MemoryRule.user_id == user_id,
            MemoryRule.is_active == True
        ).limit(3).all()
        patterns = "\n".join([f"- {r.rule_value}" for r in memory_rules]) or "None yet"
        
        # If blocker, try to get RAG guidance
        rag_resources = []
        if blockers:
            rag_resources = await self._get_rag_guidance(blockers)
        
        # Process with LLM
        try:
            prompt = CHECKIN_PROMPT_TEMPLATE.format(
                yesterday=yesterday or "Not specified",
                today=today or "Not specified",
                blockers=blockers or "None",
                today_tasks="\n".join(today_tasks) if today_tasks else "No tasks planned",
                goal=commitment.goal,
                current_week=current_week,
                weeks_remaining=weeks_remaining,
                patterns=patterns,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "assessment": {"type": "string"},
                        "next_task": {"type": "string"},
                        "next_task_timebox": {"type": "integer"},
                        "fallback_task": {"type": "string"},
                        "blocker_advice": {"type": "string"},
                        "motivation_note": {"type": "string"},
                    },
                    "required": ["assessment", "next_task", "fallback_task"],
                },
                system_prompt=CHECKIN_SYSTEM_PROMPT,
            )
            
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            llm_response = {
                "assessment": "Check-in received",
                "next_task": "Continue with your planned learning",
                "next_task_timebox": 45,
                "fallback_task": "Review yesterday's concepts for 15 minutes",
                "blocker_advice": "Try breaking the problem into smaller steps" if blockers else None,
                "motivation_note": "Keep up the momentum!",
            }
        
        # Determine advice content
        advice_text = llm_response.get("blocker_advice") or llm_response.get("motivation_note")

        # Save check-in
        checkin = Checkin(
            user_id=user_id,
            date=date.today(),
            yesterday=yesterday,
            today=today,
            blockers=blockers,
            next_task=llm_response.get("next_task"),
            fallback_task=llm_response.get("fallback_task"),
            advice=advice_text,
        )
        self.db.add(checkin)
        self.db.commit()
        
        # Update memory if pattern detected
        await self._update_memory_rules(user_id, yesterday, blockers)
        
        # Calculate adherence based on yesterday's completion
        adherence = 0.8 if yesterday and len(yesterday) > 10 else 0.5
        
        # Build response
        next_tasks = [
            {
                "task": llm_response.get("next_task", "Continue learning"),
                "timebox_min": llm_response.get("next_task_timebox", 45),
                "type": "reading",
            }
        ]
        
        if llm_response.get("fallback_task"):
            next_tasks.append({
                "task": f"[Fallback] {llm_response['fallback_task']}",
                "timebox_min": 20,
                "type": "review",
            })
        
        return AgentDecision(
            reason=llm_response.get("assessment", "Check-in processed"),
            advice=advice_text,
            signals=Signals(
                adherence=adherence,
                knowledge=0.5,
                retention=0.5,
                status="active" if not blockers else "at_risk",
            ),
            action={
                "plan_adjustment": "keep",
                "risk_mitigation": ["address_blocker"] if blockers else [],
            },
            next_tasks=next_tasks,
            resources_used=rag_resources,
            quality_score=1.0,
            quality_flags=[],
        )
    
    async def _get_rag_guidance(self, blocker: str) -> list:
        """Get RAG guidance for a blocker."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.RAG_WORKER_URL}/v1/retrieve",
                    json={"query": blocker, "top_k": 3},
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("citations", [])
        except Exception as e:
            logger.warning("RAG service unavailable", error=str(e))
        return []
    
    async def _update_memory_rules(
        self,
        user_id: int,
        yesterday: Optional[str],
        blockers: Optional[str],
    ):
        """Update memory rules based on check-in patterns."""
        # Simple pattern detection - can be enhanced with LLM
        
        # Check for skipping pattern
        if not yesterday or yesterday.lower() in ["nothing", "didn't do anything", "skipped"]:
            await self._add_or_update_rule(
                user_id,
                "task_skip",
                "User skipped learning session",
            )
        
        # Check for blocker pattern
        if blockers and "time" in blockers.lower():
            await self._add_or_update_rule(
                user_id,
                "time_constraint",
                "User frequently has time constraints - prefer shorter tasks",
            )
    
    async def _add_or_update_rule(
        self,
        user_id: int,
        rule_type: str,
        rule_value: str,
    ):
        """Add or update a memory rule."""
        existing = self.db.query(MemoryRule).filter(
            MemoryRule.user_id == user_id,
            MemoryRule.rule_type == rule_type,
        ).first()
        
        if existing:
            existing.confidence = min(1.0, existing.confidence + 0.1)
        else:
            rule = MemoryRule(
                user_id=user_id,
                rule_type=rule_type,
                rule_value=rule_value,
                confidence=0.5,
            )
            self.db.add(rule)
        
        self.db.commit()
