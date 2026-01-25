"""SQLAlchemy database models."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.db.base import Base
import enum


# Enums
class LearningStyle(str, enum.Enum):
    READING = "reading"
    CODING = "coding"
    MIXED = "mixed"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class TaskType(str, enum.Enum):
    READING = "reading"
    CODING = "coding"
    REVIEW = "review"
    QUIZ = "quiz"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    AT_RISK = "at_risk"
    RECOVERING = "recovering"


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"


class EmailType(str, enum.Enum):
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    PROGRESS_REPORT = "progress_report"
    CHECK_IN_REMINDER = "check_in_reminder"


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# Models
class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    commitments: Mapped[List["Commitment"]] = relationship(back_populates="user")
    plans: Mapped[List["Plan"]] = relationship(back_populates="user")
    checkins: Mapped[List["Checkin"]] = relationship(back_populates="user")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="user")
    coding_challenges: Mapped[List["CodingChallenge"]] = relationship(back_populates="user")
    concept_mastery: Mapped[List["ConceptMastery"]] = relationship(back_populates="user")
    memory_rules: Mapped[List["MemoryRule"]] = relationship(back_populates="user")
    agent_runs: Mapped[List["AgentRun"]] = relationship(back_populates="user")
    email_logs: Mapped[List["EmailLog"]] = relationship(back_populates="user")


class Commitment(Base):
    """Learning commitment contract."""

    __tablename__ = "commitments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Goal details
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    weekly_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # User profile
    background: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # student/professional
    baseline_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # beginner/intermediate/advanced
    learning_style: Mapped[LearningStyle] = mapped_column(
        SQLEnum(LearningStyle), default=LearningStyle.MIXED
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="commitments")
    premortem_risks: Mapped[List["PremortermRisk"]] = relationship(back_populates="commitment")


class PremortermRisk(Base):
    """Premortem risk assessment."""

    __tablename__ = "premortem_risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commitment_id: Mapped[int] = mapped_column(
        ForeignKey("commitments.id"), nullable=False, index=True
    )
    
    risk: Mapped[str] = mapped_column(Text, nullable=False)
    mitigation: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1 = highest
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    commitment: Mapped["Commitment"] = relationship(back_populates="premortem_risks")


class Plan(Base):
    """Weekly learning plan (versioned)."""

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    plan_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="plans")
    daily_tasks: Mapped[List["DailyTask"]] = relationship(back_populates="plan")


class DailyTask(Base):
    """Daily tasks derived from weekly plan."""

    __tablename__ = "daily_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)
    
    date: Mapped[date] = mapped_column(Date, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    timebox_min: Mapped[int] = mapped_column(Integer, nullable=False)  # 20, 45, or 90
    task_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType), default=TaskType.READING)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    
    # Completion tracking
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    plan: Mapped["Plan"] = relationship(back_populates="daily_tasks")


class Checkin(Base):
    """Daily standup check-in."""

    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    date: Mapped[date] = mapped_column(Date, nullable=False)
    yesterday: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    today: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blockers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Agent response
    next_task: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fallback_task: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="checkins")
    retrieval_logs: Mapped[List["RetrievalLog"]] = relationship(back_populates="checkin")


class Resource(Base):
    """Curated learning resource for RAG."""

    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    topic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # course, docs, blog
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # beginner, intermediate, advanced
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RetrievalLog(Base):
    """RAG retrieval log for observability."""

    __tablename__ = "retrieval_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkin_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("checkins.id"), nullable=True, index=True
    )
    
    query: Mapped[str] = mapped_column(Text, nullable=False)
    hits_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    citations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    checkin: Mapped[Optional["Checkin"]] = relationship(back_populates="retrieval_logs")


class Quiz(Base):
    """Weekly evaluation quiz."""

    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="quizzes")
    questions: Mapped[List["QuizQuestion"]] = relationship(back_populates="quiz")


class QuizQuestion(Base):
    """Quiz question (persisted per user)."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False, index=True)
    
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType), default=QuestionType.MCQ
    )
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For MCQ
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    
    concept: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    attempts: Mapped[List["QuizAttempt"]] = relationship(back_populates="question")


class QuizAttempt(Base):
    """Quiz question attempt."""

    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_questions.id"), nullable=False, index=True
    )
    
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    question: Mapped["QuizQuestion"] = relationship(back_populates="attempts")


class CodingChallenge(Base):
    """Coding challenge problem."""

    __tablename__ = "coding_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)  # python, javascript, etc.
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy, medium, hard
    
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=False)
    solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    concept: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="coding_challenges")
    submissions: Mapped[List["CodeSubmission"]] = relationship(back_populates="challenge")


class CodeSubmission(Base):
    """Code submission for a challenge."""

    __tablename__ = "code_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("coding_challenges.id"), nullable=False, index=True
    )
    
    code: Mapped[str] = mapped_column(Text, nullable=False)
    passed_tests: Mapped[int] = mapped_column(Integer, default=0)
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    challenge: Mapped["CodingChallenge"] = relationship(back_populates="submissions")


class ConceptMastery(Base):
    """Concept mastery tracking for retention."""

    __tablename__ = "concept_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    concept: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    times_seen: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    times_wrong: Mapped[int] = mapped_column(Integer, default=0)
    
    # Spaced repetition
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    interval_days: Mapped[int] = mapped_column(Integer, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="concept_mastery")


class MemoryRule(Base):
    """Deterministic memory rules (stable lessons)."""

    __tablename__ = "memory_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Examples:
    # rule_type: "task_preference", rule_value: "User skips tasks > 30 mins"
    # rule_type: "confusion", rule_value: "Confuses gradient descent with gradient boosting"
    # rule_type: "learning_style", rule_value: "Needs coding-first to retain concepts"
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="memory_rules")


class AgentRun(Base):
    """Agent run history for observability."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decision_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Metrics
    adherence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    knowledge_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retention_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Opik tracing
    opik_trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="agent_runs")


class EmailLog(Base):
    """Email notification log."""

    __tablename__ = "email_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    email_type: Mapped[EmailType] = mapped_column(SQLEnum(EmailType), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    
    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus), default=EmailStatus.PENDING
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="email_logs")
