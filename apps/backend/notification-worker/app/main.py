"""Notification Worker API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from shared.observability import RequestIdMiddleware, setup_logging, get_logger
from shared.db import get_session
from app.core.config import settings
from app.services import EmailService


setup_logging(level=settings.LOG_LEVEL, json_format=False, service_name="notification-worker")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Notification Worker starting", port=settings.NOTIFICATION_PORT)
    yield
    logger.info("Notification Worker shutting down")


app = FastAPI(
    title="Learning Resolution Coach - Notification Worker",
    description="Email notification service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas
class WelcomeEmailRequest(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    user_id: int
    email: EmailStr
    reset_token: str


class ProgressReportRequest(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None
    metrics: dict


class CheckinReminderRequest(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None


# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-worker"}


@app.post("/v1/email/welcome")
async def send_welcome_email(
    request: WelcomeEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    """Send welcome email to new user."""
    service = EmailService(db)
    
    # Run in background to not block
    background_tasks.add_task(
        service.send_welcome,
        user_id=request.user_id,
        email=request.email,
        name=request.name,
    )
    
    return {"message": "Welcome email queued", "status": "pending"}


@app.post("/v1/email/password-reset")
async def send_password_reset_email(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    """Send password reset email."""
    service = EmailService(db)
    
    background_tasks.add_task(
        service.send_password_reset,
        user_id=request.user_id,
        email=request.email,
        reset_token=request.reset_token,
    )
    
    return {"message": "Password reset email queued", "status": "pending"}


@app.post("/v1/email/progress-report")
async def send_progress_report(
    request: ProgressReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    """Send weekly progress report."""
    service = EmailService(db)
    
    background_tasks.add_task(
        service.send_progress_report,
        user_id=request.user_id,
        email=request.email,
        name=request.name,
        metrics=request.metrics,
    )
    
    return {"message": "Progress report email queued", "status": "pending"}


@app.post("/v1/email/checkin-reminder")
async def send_checkin_reminder(
    request: CheckinReminderRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    """Send check-in reminder email."""
    service = EmailService(db)
    
    background_tasks.add_task(
        service.send_checkin_reminder,
        user_id=request.user_id,
        email=request.email,
        name=request.name,
    )
    
    return {"message": "Check-in reminder email queued", "status": "pending"}


@app.get("/v1/email/logs/{user_id}")
async def get_email_logs(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    """Get email logs for a user."""
    from shared.db.models import EmailLog
    
    logs = db.query(EmailLog).filter(
        EmailLog.user_id == user_id
    ).order_by(EmailLog.created_at.desc()).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "type": log.email_type.value,
                "subject": log.subject,
                "status": log.status.value,
                "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
    }
