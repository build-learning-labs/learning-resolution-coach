"""API v1 routes for Core Agent."""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date

from shared.db import get_session
from shared.schemas import AgentDecision
from app.services import IntakeService, PremortermService, PlanService, CheckinService
from app.services.scoring_service import ScoringService


router = APIRouter()


# Request/Response schemas
class IntakeRequest(BaseModel):
    """Intake request for commitment contract."""
    goal: str = Field(description="Learning goal")
    target_date: date = Field(description="Target completion date")
    weekly_hours: int = Field(ge=1, le=40, description="Hours per week")
    background: Optional[str] = Field(default=None, description="student/professional")
    baseline_level: Optional[str] = Field(default=None, description="beginner/intermediate/advanced")
    learning_style: str = Field(default="mixed", description="reading/coding/mixed")


class PremortermRequest(BaseModel):
    """Premortem request for risk assessment."""
    failure_reasons: List[str] = Field(description="Why might you fail in 4 weeks?")


class CheckinRequest(BaseModel):
    """Daily check-in request."""
    yesterday: Optional[str] = Field(default=None, description="What did you do yesterday?")
    today: Optional[str] = Field(default=None, description="What will you do today?")
    blockers: Optional[str] = Field(default=None, description="Any blockers?")


# Dependency to get user ID from header
def get_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    """Extract user ID from header (set by gateway)."""
    if not x_user_id:
        # For development, use default user
        return 1
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


# Routes
@router.post("/intake", response_model=AgentDecision)
async def create_intake(
    request: IntakeRequest,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Create intake commitment contract."""
    service = IntakeService(db)
    return await service.create_commitment(
        user_id=user_id,
        goal=request.goal,
        target_date=request.target_date,
        weekly_hours=request.weekly_hours,
        background=request.background,
        baseline_level=request.baseline_level,
        learning_style=request.learning_style,
    )


@router.post("/premortem", response_model=AgentDecision)
async def create_premortem(
    request: PremortermRequest,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Process premortem risk assessment."""
    service = PremortermService(db)
    return await service.process_premortem(
        user_id=user_id,
        failure_reasons=request.failure_reasons,
    )


@router.post("/plan/weekly", response_model=AgentDecision)
async def generate_weekly_plan(
    force: bool = False,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Generate weekly learning plan."""
    service = PlanService(db)
    return await service.generate_weekly_plan(
        user_id=user_id,
        force_regenerate=force,
    )


@router.get("/plan/current")
async def get_current_plan(
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Get current weekly plan."""
    from shared.db.models import Plan
    
    plan = db.query(Plan).filter(
        Plan.user_id == user_id,
        Plan.is_active == True
    ).first()
    
    if not plan:
        return {"message": "No active plan found", "plan": None}
    
    return {
        "plan_id": plan.id,
        "week_start": plan.week_start,
        "version": plan.version,
        "plan": plan.plan_json,
    }


@router.get("/tasks/today")
async def get_today_tasks(
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Get today's tasks."""
    service = PlanService(db)
    tasks = service.get_today_tasks(user_id)
    
    return {
        "date": date.today().isoformat(),
        "tasks": [
            {
                "id": t.id,
                "task": t.task,
                "timebox_min": t.timebox_min,
                "type": t.task_type.value,
                "status": t.status.value,
            }
            for t in tasks
        ],
    }


@router.put("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Mark a task as complete."""
    from shared.db.models import DailyTask, TaskStatus
    from datetime import datetime
    
    task = db.query(DailyTask).filter(DailyTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Task completed", "task_id": task_id}


@router.post("/checkin/daily", response_model=AgentDecision)
async def daily_checkin(
    request: CheckinRequest,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Process daily standup check-in."""
    service = CheckinService(db)
    return await service.process_checkin(
        user_id=user_id,
        yesterday=request.yesterday,
        today=request.today,
        blockers=request.blockers,
    )


@router.get("/metrics/summary")
async def get_metrics_summary(
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Get metrics summary."""
    service = ScoringService(db)
    return service.get_full_metrics(user_id)


@router.get("/commitment/current")
async def get_current_commitment(
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Get current active commitment."""
    service = IntakeService(db)
    commitment = service.get_active_commitment(user_id)
    
    if not commitment:
        return {"message": "No active commitment", "commitment": None}
    
    return {
        "id": commitment.id,
        "goal": commitment.goal,
        "target_date": commitment.target_date.isoformat(),
        "weekly_hours": commitment.weekly_hours,
        "learning_style": commitment.learning_style.value,
        "created_at": commitment.created_at.isoformat(),
    }
