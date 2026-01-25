"""Plan service for weekly and daily planning."""

import json
from datetime import date, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import Commitment, Plan, DailyTask, PremortermRisk, MemoryRule, TaskType, TaskStatus
from shared.schemas import AgentDecision, Signals
from shared.observability import get_logger, trace_function

logger = get_logger(__name__)


PLAN_SYSTEM_PROMPT = """You are an AI learning coach creating personalized weekly learning plans.
Your job is to:
1. Break down the learning goal into achievable weekly tasks
2. Consider the user's available time and learning style
3. Include a mix of theory, practice, and review
4. Account for identified risks in your planning

Create realistic, actionable plans with clear timeboxes."""


PLAN_PROMPT_TEMPLATE = """User's learning goal: {goal}
Target date: {target_date} ({weeks_remaining} weeks remaining)
Weekly hours available: {weekly_hours}
Learning style: {learning_style}
Current level: {baseline_level}
Current week: {current_week}

Previous risks identified:
{risks}

Memory rules (patterns to consider):
{memory_rules}

Create a weekly learning plan.
- Distribute tasks across all 7 days (Monday-Sunday) to build a consistent habit.
- Do NOT skip weekends unless weekly hours are very low (<5h).
- Each task should be:
- Specific and actionable
- Timeboxed (20, 45, or 90 minutes)
- Tagged as reading, coding, or review

Respond in JSON format:
{{
    "week_focus": "Main theme for this week",
    "tasks": [
        {{
            "task": "Specific task description",
            "timebox_min": 45,
            "type": "reading|coding|review",
            "day": 1
        }}
    ],
    "micro_project": "Optional small project for the week",
    "review_topics": ["Topic 1", "Topic 2"]
}}"""


class PlanService:
    """Service for weekly and daily planning."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    @trace_function(name="generate_weekly_plan", tags=["planning", "core-agent"])
    async def generate_weekly_plan(
        self,
        user_id: int,
        force_regenerate: bool = False,
    ) -> AgentDecision:
        """Generate or get weekly learning plan.
        
        Args:
            user_id: User ID
            force_regenerate: Force regeneration even if plan exists
            
        Returns:
            AgentDecision with weekly plan
        """
        logger.info("Generating weekly plan", user_id=user_id)
        
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
        
        # Calculate current week
        week_start = self._get_week_start(date.today())
        weeks_remaining = max(1, (commitment.target_date - date.today()).days // 7)
        current_week = max(1, (date.today() - commitment.created_at.date()).days // 7 + 1)
        
        # Check for existing plan
        existing_plan = self.db.query(Plan).filter(
            Plan.user_id == user_id,
            Plan.week_start == week_start,
            Plan.is_active == True
        ).first()
        
        if existing_plan and not force_regenerate:
            return self._plan_to_decision(existing_plan, commitment)
        
        # Get risks and memory rules
        risks = self.db.query(PremortermRisk).filter(
            PremortermRisk.commitment_id == commitment.id
        ).order_by(PremortermRisk.priority).limit(3).all()
        
        memory_rules = self.db.query(MemoryRule).filter(
            MemoryRule.user_id == user_id,
            MemoryRule.is_active == True
        ).all()
        
        risks_text = "\n".join([f"- {r.risk}: {r.mitigation}" for r in risks]) or "None identified"
        rules_text = "\n".join([f"- {r.rule_value}" for r in memory_rules]) or "None yet"
        
        # Generate plan with LLM
        try:
            prompt = PLAN_PROMPT_TEMPLATE.format(
                goal=commitment.goal,
                target_date=commitment.target_date,
                weeks_remaining=weeks_remaining,
                weekly_hours=commitment.weekly_hours,
                learning_style=commitment.learning_style.value,
                baseline_level=commitment.baseline_level or "beginner",
                current_week=current_week,
                risks=risks_text,
                memory_rules=rules_text,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "week_focus": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string"},
                                    "timebox_min": {"type": "integer"},
                                    "type": {"type": "string"},
                                    "day": {"type": "integer"},
                                },
                            },
                        },
                        "micro_project": {"type": "string"},
                        "review_topics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["week_focus", "tasks"],
                },
                system_prompt=PLAN_SYSTEM_PROMPT,
            )
            
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            llm_response = self._default_plan(commitment)
        
        # Deactivate old plans
        if existing_plan:
            existing_plan.is_active = False
            new_version = existing_plan.version + 1
        else:
            new_version = 1
        
        # Create new plan
        plan = Plan(
            user_id=user_id,
            week_start=week_start,
            version=new_version,
            plan_json=llm_response,
            is_active=True,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        # Create daily tasks
        self._create_daily_tasks(plan, llm_response.get("tasks", []))
        
        return self._plan_to_decision(plan, commitment)
    
    def get_today_tasks(self, user_id: int) -> List[DailyTask]:
        """Get tasks for today."""
        today = date.today()
        
        # Get active plan
        plan = self.db.query(Plan).filter(
            Plan.user_id == user_id,
            Plan.is_active == True
        ).first()
        
        if not plan:
            return []
        
        return self.db.query(DailyTask).filter(
            DailyTask.plan_id == plan.id,
            DailyTask.date == today
        ).all()
    
    def _get_week_start(self, d: date) -> date:
        """Get Monday of the week."""
        return d - timedelta(days=d.weekday())
    
    def _plan_to_decision(self, plan: Plan, commitment: Commitment) -> AgentDecision:
        """Convert plan to AgentDecision."""
        plan_data = plan.plan_json or {}
        week_focus = plan_data.get("week_focus", "Learning week")
        tasks = plan_data.get("tasks", [])
        
        next_tasks = [
            {
                "task": t.get("task", ""),
                "timebox_min": t.get("timebox_min", 45),
                "type": t.get("type", "reading"),
            }
            for t in tasks[:3]
        ]
        
        return AgentDecision(
            reason=f"Week {plan.version}: {week_focus}",
            signals=Signals(
                adherence=1.0,
                knowledge=0.0,
                retention=0.0,
                status="active",
            ),
            action={"plan_adjustment": "keep", "risk_mitigation": []},
            next_tasks=next_tasks,
            resources_used=[],
            quality_score=1.0,
            quality_flags=[],
        )
    
    def _create_daily_tasks(self, plan: Plan, tasks: List[Dict]):
        """Create DailyTask records from plan tasks."""
        week_start = plan.week_start
        
        for task_data in tasks:
            day = task_data.get("day", 1)
            task_date = week_start + timedelta(days=max(0, day - 1))
            
            task_type_str = task_data.get("type", "reading")
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                task_type = TaskType.READING
            
            daily_task = DailyTask(
                plan_id=plan.id,
                date=task_date,
                task=task_data.get("task", ""),
                timebox_min=task_data.get("timebox_min", 45),
                task_type=task_type,
                status=TaskStatus.PENDING,
            )
            self.db.add(daily_task)
        
        self.db.commit()
    
    def _default_plan(self, commitment: Commitment) -> Dict:
        """Generate default plan if LLM fails."""
        return {
            "week_focus": f"Getting started with {commitment.goal}",
            "tasks": [
                {"task": "Review fundamentals", "timebox_min": 45, "type": "reading", "day": 1},
                {"task": "Practice exercise 1", "timebox_min": 30, "type": "coding", "day": 2},
                {"task": "Continue learning", "timebox_min": 45, "type": "reading", "day": 3},
                {"task": "Practice exercise 2", "timebox_min": 30, "type": "coding", "day": 4},
                {"task": "Weekly review", "timebox_min": 20, "type": "review", "day": 5},
            ],
            "micro_project": None,
            "review_topics": [],
        }
