"""Scoring and metrics calculation."""

from datetime import date, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from shared.db.models import (
    Commitment, Plan, DailyTask, Checkin, Quiz, ConceptMastery,
    TaskStatus, UserStatus
)
from shared.observability import get_logger

logger = get_logger(__name__)


class ScoringService:
    """Service for calculating adherence, knowledge, and retention scores."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_adherence(self, user_id: int, days: int = 7) -> float:
        """Calculate task completion adherence score.
        
        Args:
            user_id: User ID
            days: Number of days to consider
            
        Returns:
            Adherence score between 0.0 and 1.0
        """
        since = date.today() - timedelta(days=days)
        
        # Get active plan
        plan = self.db.query(Plan).filter(
            Plan.user_id == user_id,
            Plan.is_active == True
        ).first()
        
        if not plan:
            return 0.0
        
        # Count tasks
        total_tasks = self.db.query(DailyTask).filter(
            DailyTask.plan_id == plan.id,
            DailyTask.date >= since,
            DailyTask.date <= date.today(),
        ).count()
        
        completed_tasks = self.db.query(DailyTask).filter(
            DailyTask.plan_id == plan.id,
            DailyTask.date >= since,
            DailyTask.date <= date.today(),
            DailyTask.status == TaskStatus.COMPLETED,
        ).count()
        
        if total_tasks == 0:
            return 1.0  # No tasks to complete
        
        return round(completed_tasks / total_tasks, 2)
    
    def calculate_knowledge(self, user_id: int) -> float:
        """Calculate knowledge score from quiz performance.
        
        Args:
            user_id: User ID
            
        Returns:
            Knowledge score between 0.0 and 1.0
        """
        # Get completed quizzes
        quizzes = self.db.query(Quiz).filter(
            Quiz.user_id == user_id,
            Quiz.completed == True,
            Quiz.score is not None,
        ).order_by(Quiz.created_at.desc()).limit(5).all()
        
        if not quizzes:
            return 0.0
        
        avg_score = sum(q.score or 0 for q in quizzes) / len(quizzes)
        return round(avg_score, 2)
    
    def calculate_retention(self, user_id: int) -> float:
        """Calculate retention score from concept mastery.
        
        Args:
            user_id: User ID
            
        Returns:
            Retention score between 0.0 and 1.0
        """
        # Get concept mastery records
        concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
        ).all()
        
        if not concepts:
            return 0.0
        
        # Calculate weighted retention
        total_seen = sum(c.times_seen for c in concepts)
        total_correct = sum(c.times_correct for c in concepts)
        
        if total_seen == 0:
            return 0.0
        
        return round(total_correct / total_seen, 2)
    
    def calculate_recovery_effectiveness(self, user_id: int) -> float:
        """Calculate how well user recovers from at_risk status.
        
        Args:
            user_id: User ID
            
        Returns:
            Recovery score between 0.0 and 1.0
        """
        # This would analyze historical status changes
        # For now, return a static value
        return 0.8
    
    def get_user_status(self, user_id: int) -> str:
        """Determine current user status based on metrics.
        
        Args:
            user_id: User ID
            
        Returns:
            Status string: 'active', 'at_risk', or 'recovering'
        """
        adherence = self.calculate_adherence(user_id)
        
        # Check recent check-ins
        recent_checkins = self.db.query(Checkin).filter(
            Checkin.user_id == user_id,
            Checkin.date >= date.today() - timedelta(days=3),
        ).count()
        
        # Status logic
        if adherence < 0.3 or recent_checkins == 0:
            return "at_risk"
        elif adherence < 0.6:
            return "recovering"
        else:
            return "active"
    
    def get_full_metrics(self, user_id: int) -> Dict:
        """Get all metrics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with all metrics
        """
        adherence = self.calculate_adherence(user_id)
        knowledge = self.calculate_knowledge(user_id)
        retention = self.calculate_retention(user_id)
        recovery = self.calculate_recovery_effectiveness(user_id)
        status = self.get_user_status(user_id)
        
        # Get current week
        commitment = self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).first()
        
        current_week = 1
        weeks_remaining = 4
        
        if commitment:
            current_week = max(1, (date.today() - commitment.created_at.date()).days // 7 + 1)
            weeks_remaining = max(0, (commitment.target_date - date.today()).days // 7)
        
        return {
            "adherence_score": adherence,
            "knowledge_score": knowledge,
            "retention_score": retention,
            "recovery_effectiveness": recovery,
            "current_week": current_week,
            "weeks_remaining": weeks_remaining,
            "status": status,
        }
