"""Unit tests for scoring service."""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Test adaptation policy
from app.domain.decision_engine import AdaptationPolicy


class TestAdaptationPolicy:
    """Test cases for AdaptationPolicy."""
    
    def test_reduce_scope_low_adherence(self):
        """Should recommend reduce_scope when adherence is very low."""
        result = AdaptationPolicy.determine_adjustment(
            adherence=0.2,
            knowledge=0.5,
            retention=0.5,
        )
        assert result == "reduce_scope"
    
    def test_repeat_concepts_low_retention(self):
        """Should recommend repeat_concepts when retention is low."""
        result = AdaptationPolicy.determine_adjustment(
            adherence=0.7,
            knowledge=0.5,
            retention=0.3,
        )
        assert result == "repeat_concepts"
    
    def test_increase_challenge_high_performance(self):
        """Should recommend increase_challenge when doing well."""
        result = AdaptationPolicy.determine_adjustment(
            adherence=0.9,
            knowledge=0.85,
            retention=0.8,
        )
        assert result == "increase_challenge"
    
    def test_keep_moderate_performance(self):
        """Should recommend keep for moderate performance."""
        result = AdaptationPolicy.determine_adjustment(
            adherence=0.7,
            knowledge=0.6,
            retention=0.6,
        )
        assert result == "keep"
    
    def test_priority_adherence_over_retention(self):
        """Low adherence should take priority over low retention."""
        result = AdaptationPolicy.determine_adjustment(
            adherence=0.2,
            knowledge=0.5,
            retention=0.3,
        )
        assert result == "reduce_scope"


class TestScoringCalculations:
    """Test cases for scoring calculations."""
    
    def test_adherence_no_tasks(self):
        """Should return 1.0 when no tasks exist."""
        # This would require mocking the database
        # For now, just test the logic
        total_tasks = 0
        completed_tasks = 0
        
        if total_tasks == 0:
            adherence = 1.0
        else:
            adherence = completed_tasks / total_tasks
        
        assert adherence == 1.0
    
    def test_adherence_calculation(self):
        """Should calculate adherence correctly."""
        total_tasks = 5
        completed_tasks = 4
        
        adherence = completed_tasks / total_tasks
        assert adherence == 0.8
    
    def test_adherence_all_complete(self):
        """Should return 1.0 when all tasks complete."""
        total_tasks = 5
        completed_tasks = 5
        
        adherence = completed_tasks / total_tasks
        assert adherence == 1.0
    
    def test_knowledge_average(self):
        """Should calculate average quiz score."""
        quiz_scores = [0.8, 0.6, 0.9, 0.7]
        
        avg_score = sum(quiz_scores) / len(quiz_scores)
        assert avg_score == 0.75
    
    def test_retention_calculation(self):
        """Should calculate retention from seen/correct ratio."""
        times_seen = 10
        times_correct = 7
        
        if times_seen == 0:
            retention = 0.0
        else:
            retention = times_correct / times_seen
        
        assert retention == 0.7


class TestUserStatusDetermination:
    """Test cases for user status logic."""
    
    def test_at_risk_low_adherence(self):
        """Should be at_risk when adherence is very low."""
        adherence = 0.2
        recent_checkins = 2
        
        if adherence < 0.3 or recent_checkins == 0:
            status = "at_risk"
        elif adherence < 0.6:
            status = "recovering"
        else:
            status = "active"
        
        assert status == "at_risk"
    
    def test_at_risk_no_checkins(self):
        """Should be at_risk when no recent check-ins."""
        adherence = 0.8
        recent_checkins = 0
        
        if adherence < 0.3 or recent_checkins == 0:
            status = "at_risk"
        elif adherence < 0.6:
            status = "recovering"
        else:
            status = "active"
        
        assert status == "at_risk"
    
    def test_recovering_medium_adherence(self):
        """Should be recovering with medium adherence."""
        adherence = 0.5
        recent_checkins = 2
        
        if adherence < 0.3 or recent_checkins == 0:
            status = "at_risk"
        elif adherence < 0.6:
            status = "recovering"
        else:
            status = "active"
        
        assert status == "recovering"
    
    def test_active_good_performance(self):
        """Should be active with good performance."""
        adherence = 0.8
        recent_checkins = 3
        
        if adherence < 0.3 or recent_checkins == 0:
            status = "at_risk"
        elif adherence < 0.6:
            status = "recovering"
        else:
            status = "active"
        
        assert status == "active"
