"""Email service for notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from shared.db.models import EmailLog, EmailType, EmailStatus
from shared.observability import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def send_email(
        self,
        user_id: int,
        to_email: str,
        subject: str,
        html_content: str,
        email_type: EmailType,
    ) -> bool:
        """Send an email and log it.
        
        Args:
            user_id: User ID
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email body
            email_type: Type of email
            
        Returns:
            True if sent successfully
        """
        logger.info("Sending email", to=to_email, type=email_type.value)
        
        # Create log entry
        log = EmailLog(
            user_id=user_id,
            email_type=email_type,
            subject=subject,
            recipient=to_email,
            status=EmailStatus.PENDING,
        )
        self.db.add(log)
        self.db.commit()
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # Send
        try:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
                
                log.status = EmailStatus.SENT
                log.sent_at = datetime.utcnow()
                logger.info("Email sent successfully", to=to_email)
            else:
                # Development mode - just log
                logger.info("Email would be sent (SMTP not configured)", to=to_email, subject=subject)
                log.status = EmailStatus.SENT
                log.sent_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            log.status = EmailStatus.FAILED
            log.error_message = str(e)
            self.db.commit()
            return False
    
    async def send_welcome(
        self,
        user_id: int,
        email: str,
        name: Optional[str] = None,
    ) -> bool:
        """Send welcome email to new user."""
        name = name or "Learner"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">Welcome to Learning Resolution Coach! 🎓</h1>
            <p>Hi {name},</p>
            <p>We're excited to help you achieve your learning goals!</p>
            <p>Here's how to get started:</p>
            <ol>
                <li>Set up your learning commitment</li>
                <li>Complete the premortem assessment</li>
                <li>Start your daily check-ins</li>
            </ol>
            <p>
                <a href="{settings.FRONTEND_URL}/dashboard" 
                   style="background: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px;">
                    Get Started
                </a>
            </p>
            <p>Happy learning!</p>
            <p><em>The Learning Resolution Coach Team</em></p>
        </body>
        </html>
        """
        
        return await self.send_email(
            user_id=user_id,
            to_email=email,
            subject="Welcome to Learning Resolution Coach! 🎓",
            html_content=html,
            email_type=EmailType.WELCOME,
        )
    
    async def send_password_reset(
        self,
        user_id: int,
        email: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Reset Your Password</h2>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to create a new password:</p>
            <p>
                <a href="{reset_url}" 
                   style="background: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px;">
                    Reset Password
                </a>
            </p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, you can safely ignore this email.</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            user_id=user_id,
            to_email=email,
            subject="Reset Your Password",
            html_content=html,
            email_type=EmailType.PASSWORD_RESET,
        )
    
    async def send_progress_report(
        self,
        user_id: int,
        email: str,
        name: Optional[str],
        metrics: dict,
    ) -> bool:
        """Send weekly progress report."""
        name = name or "Learner"
        
        adherence = metrics.get("adherence_score", 0) * 100
        knowledge = metrics.get("knowledge_score", 0) * 100
        retention = metrics.get("retention_score", 0) * 100
        week = metrics.get("current_week", 1)
        status = metrics.get("status", "active")
        
        status_emoji = "🟢" if status == "active" else "🟡" if status == "recovering" else "🔴"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">Your Week {week} Progress Report 📊</h1>
            <p>Hi {name},</p>
            <p>Here's how you did this week:</p>
            
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Adherence:</strong> {adherence:.0f}%</p>
                <p><strong>Knowledge:</strong> {knowledge:.0f}%</p>
                <p><strong>Retention:</strong> {retention:.0f}%</p>
                <p><strong>Status:</strong> {status_emoji} {status.title()}</p>
            </div>
            
            <p>
                <a href="{settings.FRONTEND_URL}/dashboard" 
                   style="background: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px;">
                    View Full Dashboard
                </a>
            </p>
            
            <p>Keep up the momentum!</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            user_id=user_id,
            to_email=email,
            subject=f"Week {week} Progress Report 📊",
            html_content=html,
            email_type=EmailType.PROGRESS_REPORT,
        )
    
    async def send_checkin_reminder(
        self,
        user_id: int,
        email: str,
        name: Optional[str],
    ) -> bool:
        """Send check-in reminder."""
        name = name or "Learner"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Time for Your Daily Check-in! ⏰</h2>
            <p>Hi {name},</p>
            <p>Don't forget to do your daily check-in to stay on track with your learning goals.</p>
            <p>It only takes a minute!</p>
            <p>
                <a href="{settings.FRONTEND_URL}/checkin" 
                   style="background: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px;">
                    Do Check-in Now
                </a>
            </p>
        </body>
        </html>
        """
        
        return await self.send_email(
            user_id=user_id,
            to_email=email,
            subject="Time for Your Daily Check-in! ⏰",
            html_content=html,
            email_type=EmailType.CHECK_IN_REMINDER,
        )
