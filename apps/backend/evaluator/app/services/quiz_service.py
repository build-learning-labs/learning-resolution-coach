"""Quiz service for evaluation."""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import Quiz, QuizQuestion, QuizAttempt, ConceptMastery, QuestionType
from shared.observability import get_logger

logger = get_logger(__name__)


QUIZ_GENERATION_PROMPT = """Generate a quiz for testing knowledge on: {topic}

User's current level: {level}
Recent concepts covered: {concepts}

Create {num_questions} questions that test understanding, not just memorization.
Mix question types: some multiple choice, some short answer.

Respond in JSON format:
{{
    "topic": "{topic}",
    "questions": [
        {{
            "question": "Clear question text",
            "type": "mcq",
            "options": {{"A": "option A", "B": "option B", "C": "option C", "D": "option D"}},
            "correct_answer": "A",
            "concept": "Specific concept being tested"
        }},
        {{
            "question": "Short answer question",
            "type": "short_answer",
            "options": null,
            "correct_answer": "Expected answer or key points",
            "concept": "Concept being tested"
        }}
    ]
}}"""


JUDGE_PROMPT = """You are evaluating a student's answer to a quiz question.

Question: {question}
Correct Answer: {correct_answer}
Student's Answer: {user_answer}
Concept: {concept}

Evaluate the student's answer and provide:
1. Score (0.0 to 1.0)
2. Brief feedback explaining what was correct/incorrect
3. Whether the concept is understood

Respond in JSON format:
{{
    "score": 0.8,
    "feedback": "Your explanation of why the answer is correct/incorrect",
    "concept_understood": true
}}"""


class QuizService:
    """Service for quiz generation and evaluation."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    async def generate_quiz(
        self,
        user_id: int,
        topic: str,
        num_questions: int = 5,
        level: str = "intermediate",
    ) -> Dict:
        """Generate a new quiz for a topic.
        
        Args:
            user_id: User ID
            topic: Topic to create quiz for
            num_questions: Number of questions
            level: Difficulty level
            
        Returns:
            Quiz data with questions
        """
        logger.info("Generating quiz", user_id=user_id, topic=topic, num_questions=num_questions)
        
        # Get weak concepts for this user
        weak_concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.times_seen > 0,
        ).order_by(
            (ConceptMastery.times_correct / ConceptMastery.times_seen).asc()
        ).limit(3).all()
        
        concepts_text = ", ".join([c.concept for c in weak_concepts]) if weak_concepts else "general concepts"
        
        # Get current week
        from shared.db.models import Commitment
        from datetime import date
        
        commitment = self.db.query(Commitment).filter(
            Commitment.user_id == user_id,
            Commitment.is_active == True
        ).first()
        
        week = 1
        if commitment:
            week = max(1, (date.today() - commitment.created_at.date()).days // 7 + 1)
        
        # Generate with LLM
        try:
            prompt = QUIZ_GENERATION_PROMPT.format(
                topic=topic,
                level=level,
                concepts=concepts_text,
                num_questions=num_questions,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "type": {"type": "string"},
                                    "options": {"type": "object"},
                                    "correct_answer": {"type": "string"},
                                    "concept": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["topic", "questions"],
                },
            )
            
        except Exception as e:
            logger.error("LLM quiz generation failed", error=str(e))
            llm_response = self._default_quiz(topic, num_questions)
        
        # Create quiz record
        quiz = Quiz(
            user_id=user_id,
            week=week,
            topic=topic,
            score=None,
            completed=False,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        
        # Create question records
        questions_data = []
        for q in llm_response.get("questions", []):
            q_type = QuestionType.MCQ if q.get("type") == "mcq" else QuestionType.SHORT_ANSWER
            
            question = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get("question", ""),
                question_type=q_type,
                options=q.get("options"),
                correct_answer=q.get("correct_answer", ""),
                concept=q.get("concept"),
            )
            self.db.add(question)
            self.db.commit()
            self.db.refresh(question)
            
            questions_data.append({
                "id": question.id,
                "question": question.question,
                "type": question.question_type.value,
                "options": question.options,
                "concept": question.concept,
            })
        
        return {
            "quiz_id": quiz.id,
            "topic": topic,
            "questions": questions_data,
        }
    
    async def submit_quiz(
        self,
        quiz_id: int,
        answers: List[Dict],
    ) -> Dict:
        """Submit quiz answers for grading.
        
        Args:
            quiz_id: Quiz ID
            answers: List of {question_id: answer} dicts
            
        Returns:
            Grading results with scores and feedback
        """
        logger.info("Grading quiz", quiz_id=quiz_id, num_answers=len(answers))
        
        quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return {"error": "Quiz not found"}
        
        questions = self.db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).all()
        
        questions_by_id = {q.id: q for q in questions}
        
        total_score = 0.0
        results = []
        
        for answer in answers:
            question_id = answer.get("question_id")
            user_answer = answer.get("answer", "")
            
            question = questions_by_id.get(question_id)
            if not question:
                continue
            
            # Grade with LLM
            try:
                judge_prompt = JUDGE_PROMPT.format(
                    question=question.question,
                    correct_answer=question.correct_answer,
                    user_answer=user_answer,
                    concept=question.concept or "general",
                )
                
                judge_response = await self.llm.structured_output(
                    prompt=judge_prompt,
                    schema={
                        "type": "object",
                        "properties": {
                            "score": {"type": "number"},
                            "feedback": {"type": "string"},
                            "concept_understood": {"type": "boolean"},
                        },
                        "required": ["score", "feedback"],
                    },
                )
                
                score = judge_response.get("score", 0.0)
                feedback = judge_response.get("feedback", "")
                understood = judge_response.get("concept_understood", score > 0.6)
                
            except Exception as e:
                logger.error("LLM judging failed", error=str(e))
                # Simple fallback: exact match gives 1.0, partial 0.5
                if user_answer.lower().strip() == question.correct_answer.lower().strip():
                    score = 1.0
                elif question.correct_answer.lower() in user_answer.lower():
                    score = 0.5
                else:
                    score = 0.0
                feedback = "Answer evaluated"
                understood = score > 0.5
            
            # Record attempt
            attempt = QuizAttempt(
                question_id=question_id,
                user_answer=user_answer,
                score=score,
                feedback=feedback,
            )
            self.db.add(attempt)
            
            # Update concept mastery
            if question.concept:
                await self._update_concept_mastery(
                    quiz.user_id,
                    question.concept,
                    understood,
                )
            
            total_score += score
            results.append({
                "question_id": question_id,
                "score": score,
                "feedback": feedback,
                "correct_answer": question.correct_answer,
                "concept_understood": understood,
            })
        
        # Update quiz
        avg_score = total_score / len(answers) if answers else 0.0
        quiz.score = avg_score
        quiz.completed = True
        self.db.commit()
        
        return {
            "quiz_id": quiz_id,
            "score": avg_score,
            "results": results,
        }
    
    async def _update_concept_mastery(
        self,
        user_id: int,
        concept: str,
        understood: bool,
    ):
        """Update concept mastery tracking."""
        mastery = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.concept == concept,
        ).first()
        
        if mastery:
            mastery.times_seen += 1
            if understood:
                mastery.times_correct += 1
            else:
                mastery.times_wrong += 1
        else:
            mastery = ConceptMastery(
                user_id=user_id,
                concept=concept,
                times_seen=1,
                times_correct=1 if understood else 0,
                times_wrong=0 if understood else 1,
            )
            self.db.add(mastery)
        
        self.db.commit()
    
    def _default_quiz(self, topic: str, num_questions: int) -> Dict:
        """Fallback quiz if LLM fails."""
        return {
            "topic": topic,
            "questions": [
                {
                    "question": f"Explain the key concept of {topic}",
                    "type": "short_answer",
                    "options": None,
                    "correct_answer": "Understanding of core concepts",
                    "concept": topic,
                }
                for _ in range(min(num_questions, 3))
            ],
        }
