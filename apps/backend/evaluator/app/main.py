"""Evaluator API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from shared.observability import RequestIdMiddleware, setup_logging, get_logger
from shared.db import get_session
from app.core.config import settings
from app.services import QuizService, CodingService


setup_logging(level=settings.LOG_LEVEL, json_format=False, service_name="evaluator")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Evaluator service starting", port=settings.EVALUATOR_PORT)
    yield
    logger.info("Evaluator service shutting down")


app = FastAPI(
    title="Learning Resolution Coach - Evaluator",
    description="Quiz, coding challenges, and LLM judge",
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
class QuizGenerateRequest(BaseModel):
    topic: str
    num_questions: int = 5
    level: str = "intermediate"


class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: List[dict]  # [{question_id: int, answer: str}]


class CodingGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    language: str = "python"


class CodeSubmitRequest(BaseModel):
    challenge_id: int
    code: str


# Dependency
def get_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    if not x_user_id:
        return 1
    return int(x_user_id)


# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "evaluator"}


@app.post("/v1/eval/quiz/generate")
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Generate a quiz for the given topic."""
    service = QuizService(db)
    return await service.generate_quiz(
        user_id=user_id,
        topic=request.topic,
        num_questions=request.num_questions,
        level=request.level,
    )


@app.post("/v1/eval/quiz/submit")
async def submit_quiz(
    request: QuizSubmitRequest,
    db: Session = Depends(get_session),
):
    """Submit quiz answers for grading."""
    service = QuizService(db)
    return await service.submit_quiz(
        quiz_id=request.quiz_id,
        answers=request.answers,
    )


@app.get("/v1/quiz/{quiz_id}")
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_session),
):
    """Get quiz details."""
    from shared.db.models import Quiz, QuizQuestion
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return {"error": "Quiz not found"}
    
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()
    
    return {
        "quiz_id": quiz.id,
        "topic": quiz.topic,
        "completed": quiz.completed,
        "score": quiz.score,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "type": q.question_type.value,
                "options": q.options,
            }
            for q in questions
        ],
    }


@app.post("/v1/coding/generate")
async def generate_coding_challenge(
    request: CodingGenerateRequest,
    db: Session = Depends(get_session),
    user_id: int = Depends(get_user_id),
):
    """Generate a coding challenge."""
    service = CodingService(db)
    return await service.generate_challenge(
        user_id=user_id,
        topic=request.topic,
        difficulty=request.difficulty,
        language=request.language,
    )


@app.post("/v1/coding/submit")
async def submit_code(
    request: CodeSubmitRequest,
    db: Session = Depends(get_session),
):
    """Submit code for evaluation."""
    service = CodingService(db)
    return await service.submit_code(
        challenge_id=request.challenge_id,
        code=request.code,
    )


@app.get("/v1/coding/{challenge_id}")
async def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_session),
):
    """Get challenge details."""
    service = CodingService(db)
    challenge = service.get_challenge(challenge_id)
    
    if not challenge:
        return {"error": "Challenge not found"}
    
    return {
        "challenge_id": challenge.id,
        "title": challenge.title,
        "problem": challenge.problem,
        "language": challenge.language,
        "difficulty": challenge.difficulty,
        "starter_code": challenge.starter_code,
    }


@app.get("/v1/retention/{user_id}")
async def get_retention_data(
    user_id: int,
    db: Session = Depends(get_session),
):
    """Get concept mastery/retention data for a user."""
    from shared.db.models import ConceptMastery
    
    concepts = db.query(ConceptMastery).filter(
        ConceptMastery.user_id == user_id
    ).order_by(ConceptMastery.times_seen.desc()).all()
    
    return {
        "user_id": user_id,
        "concepts": [
            {
                "concept": c.concept,
                "times_seen": c.times_seen,
                "times_correct": c.times_correct,
                "times_wrong": c.times_wrong,
                "mastery": c.times_correct / c.times_seen if c.times_seen > 0 else 0,
                "next_review": c.next_review_at.isoformat() if c.next_review_at else None,
            }
            for c in concepts
        ],
    }
