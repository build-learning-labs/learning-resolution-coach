"""Decision engine for agent actions and adaptations."""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from shared.db.models import MemoryRule, PremortermRisk, Commitment
from shared.schemas import AgentDecision, Signals
from app.services.scoring_service import ScoringService
from shared.observability import get_logger

logger = get_logger(__name__)


class AdaptationPolicy:
    """Policy definitions for plan adaptations."""
    
    # Threshold definitions
    LOW_ADHERENCE_THRESHOLD = 0.3
    MEDIUM_ADHERENCE_THRESHOLD = 0.6
    LOW_KNOWLEDGE_THRESHOLD = 0.4
    LOW_RETENTION_THRESHOLD = 0.5
    
    @classmethod
    def determine_adjustment(
        cls,
        adherence: float,
        knowledge: float,
        retention: float,
    ) -> str:
        """Determine plan adjustment based on scores.
        
        Returns:
            One of: 'reduce_scope', 'repeat_concepts', 'increase_challenge', 'keep'
        """
        if adherence < cls.LOW_ADHERENCE_THRESHOLD:
            return "reduce_scope"
        
        if retention < cls.LOW_RETENTION_THRESHOLD:
            return "repeat_concepts"
        
        if knowledge > 0.8 and adherence > 0.8:
            return "increase_challenge"
        
        return "keep"


class DecisionEngine:
    """Engine for generating agent decisions based on current state."""
    
    def __init__(self, db: Session):
        self.db = db
        self.scoring = ScoringService(db)
    
    def get_signals(self, user_id: int) -> Signals:
        """Get current signals for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Signals object with current metrics
        """
        metrics = self.scoring.get_full_metrics(user_id)
        
        return Signals(
            adherence=metrics["adherence_score"],
            knowledge=metrics["knowledge_score"],
            retention=metrics["retention_score"],
            status=metrics["status"],
        )
    
    def get_active_mitigations(self, user_id: int) -> List[str]:
        """Get active risk mitigations for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active mitigation strategies
        """
        # Get commitment
        commitment = self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).first()
        
        if not commitment:
            return []
        
        # Get risks with mitigations
        risks = self.db.query(PremortermRisk).filter(
            PremortermRisk.commitment_id == commitment.id
        ).order_by(PremortermRisk.priority).limit(3).all()
        
        return [r.mitigation for r in risks if r.mitigation]
    
    def get_memory_rules(self, user_id: int) -> List[MemoryRule]:
        """Get active memory rules for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active memory rules
        """
        return self.db.query(MemoryRule).filter(
            MemoryRule.user_id == user_id,
            MemoryRule.is_active == True
        ).order_by(MemoryRule.confidence.desc()).all()
    
    def generate_action(self, user_id: int) -> Dict:
        """Generate recommended action based on current state.
        
        Args:
            user_id: User ID
            
        Returns:
            Action dictionary with plan_adjustment and risk_mitigation
        """
        signals = self.get_signals(user_id)
        
        adjustment = AdaptationPolicy.determine_adjustment(
            signals.adherence,
            signals.knowledge,
            signals.retention,
        )
        
        mitigations = self.get_active_mitigations(user_id)
        
        # Add status-based mitigations
        if signals.status == "at_risk":
            if "check_in_reminder" not in mitigations:
                mitigations.append("check_in_reminder")
        
        return {
            "plan_adjustment": adjustment,
            "risk_mitigation": mitigations[:3],  # Max 3 active mitigations
        }
    
    def build_decision(
        self,
        user_id: int,
        reason: str,
        next_tasks: List[Dict],
        resources_used: Optional[List[Dict]] = None,
        quality_score: float = 1.0,
        quality_flags: Optional[List[str]] = None,
    ) -> AgentDecision:
        """Build a complete AgentDecision.
        
        Args:
            user_id: User ID
            reason: Explanation for the decision
            next_tasks: List of recommended tasks
            resources_used: Optional RAG citations
            quality_score: Critic quality score
            quality_flags: Any quality issues
            
        Returns:
            Complete AgentDecision object
        """
        return AgentDecision(
            reason=reason,
            signals=self.get_signals(user_id),
            action=self.generate_action(user_id),
            next_tasks=next_tasks,
            resources_used=resources_used or [],
            quality_score=quality_score,
            quality_flags=quality_flags or [],
        )
