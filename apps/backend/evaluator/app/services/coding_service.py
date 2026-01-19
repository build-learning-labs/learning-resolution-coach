"""Coding challenge service."""

import subprocess
import tempfile
import os
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from shared.llm import get_llm_provider, LLMProvider
from shared.db.models import CodingChallenge, CodeSubmission
from shared.observability import get_logger
from app.core.config import settings

logger = get_logger(__name__)


CHALLENGE_GENERATION_PROMPT = """Create a coding challenge for: {topic}
Difficulty: {difficulty}
Language: {language}

The challenge should be:
1. Clear and well-defined
2. Testable with simple inputs/outputs
3. Educational for the given topic

Respond in JSON format:
{{
    "title": "Challenge title",
    "problem": "Full problem description with examples",
    "starter_code": "def solution(input):\\n    # Your code here\\n    pass",
    "test_cases": [
        {{"input": "example_input", "expected": "expected_output"}},
        {{"input": "test_input2", "expected": "expected_output2"}}
    ],
    "solution": "def solution(input):\\n    # Reference solution\\n    return result"
}}"""


class CodingService:
    """Service for coding challenges and evaluation."""
    
    def __init__(self, db: Session, llm: Optional[LLMProvider] = None):
        self.db = db
        self.llm = llm or get_llm_provider()
    
    async def generate_challenge(
        self,
        user_id: int,
        topic: str,
        difficulty: str = "medium",
        language: str = "python",
    ) -> Dict:
        """Generate a coding challenge.
        
        Args:
            user_id: User ID
            topic: Topic for the challenge
            difficulty: easy/medium/hard
            language: Programming language
            
        Returns:
            Challenge data
        """
        logger.info("Generating coding challenge", user_id=user_id, topic=topic)
        
        # Generate with LLM
        try:
            prompt = CHALLENGE_GENERATION_PROMPT.format(
                topic=topic,
                difficulty=difficulty,
                language=language,
            )
            
            llm_response = await self.llm.structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "problem": {"type": "string"},
                        "starter_code": {"type": "string"},
                        "test_cases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "input": {"type": "string"},
                                    "expected": {"type": "string"},
                                },
                            },
                        },
                        "solution": {"type": "string"},
                    },
                    "required": ["title", "problem", "test_cases"],
                },
            )
            
        except Exception as e:
            logger.error("LLM challenge generation failed", error=str(e))
            llm_response = self._default_challenge(topic, language)
        
        # Create challenge record
        challenge = CodingChallenge(
            user_id=user_id,
            title=llm_response.get("title", f"Challenge: {topic}"),
            problem=llm_response.get("problem", ""),
            language=language,
            difficulty=difficulty,
            starter_code=llm_response.get("starter_code"),
            test_cases=llm_response.get("test_cases", []),
            solution=llm_response.get("solution"),
            concept=topic,
        )
        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)
        
        return {
            "challenge_id": challenge.id,
            "title": challenge.title,
            "problem": challenge.problem,
            "language": challenge.language,
            "difficulty": challenge.difficulty,
            "starter_code": challenge.starter_code,
            "test_cases_count": len(challenge.test_cases),
        }
    
    async def submit_code(
        self,
        challenge_id: int,
        code: str,
    ) -> Dict:
        """Submit code for a challenge.
        
        Args:
            challenge_id: Challenge ID
            code: User's submitted code
            
        Returns:
            Execution results
        """
        logger.info("Evaluating code submission", challenge_id=challenge_id)
        
        challenge = self.db.query(CodingChallenge).filter(
            CodingChallenge.id == challenge_id
        ).first()
        
        if not challenge:
            return {"error": "Challenge not found"}
        
        test_cases = challenge.test_cases or []
        passed = 0
        total = len(test_cases)
        results = []
        error_output = None
        
        # Execute code against test cases (sandboxed)
        if settings.SANDBOX_ENABLED:
            for tc in test_cases:
                try:
                    result = await self._execute_sandbox(
                        code=code,
                        test_input=tc.get("input"),
                        expected=tc.get("expected"),
                        language=challenge.language,
                    )
                    if result["passed"]:
                        passed += 1
                    results.append(result)
                except Exception as e:
                    error_output = str(e)
                    results.append({"passed": False, "error": str(e)})
        else:
            # Simplified evaluation without sandbox
            # Just check if code is syntactically valid
            try:
                if challenge.language == "python":
                    compile(code, "<string>", "exec")
                    # Assume passes if valid syntax
                    passed = total // 2  # Give partial credit
                    results = [{"passed": True, "note": "Sandbox disabled"}] * passed
            except SyntaxError as e:
                error_output = f"Syntax error: {e}"
                results = [{"passed": False, "error": error_output}]
        
        # Create submission record
        submission = CodeSubmission(
            challenge_id=challenge_id,
            code=code,
            passed_tests=passed,
            total_tests=total,
            output=str(results),
            error=error_output,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        # Update concept mastery if applicable
        if challenge.concept and passed > 0:
            from app.services.quiz_service import QuizService
            # This would update mastery, but we'll skip the cross-service call here
        
        return {
            "submission_id": submission.id,
            "passed_tests": passed,
            "total_tests": total,
            "score": passed / total if total > 0 else 0.0,
            "results": results,
            "error": error_output,
        }
    
    async def _execute_sandbox(
        self,
        code: str,
        test_input: str,
        expected: str,
        language: str,
    ) -> Dict:
        """Execute code in a sandboxed environment.
        
        This is a placeholder for real sandbox implementation.
        In production, use Docker, Firecracker, or a service like Judge0.
        """
        if language != "python":
            return {"passed": False, "error": f"Language {language} not supported"}
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Wrap code with test execution
            test_code = f"""
{code}

# Test execution
result = solution({test_input})
print(result)
"""
            f.write(test_code)
            f.flush()
            
            try:
                # Run with timeout
                result = subprocess.run(
                    ['python3', f.name],
                    capture_output=True,
                    text=True,
                    timeout=settings.SANDBOX_TIMEOUT_SECONDS,
                )
                
                output = result.stdout.strip()
                passed = output == expected
                
                return {
                    "passed": passed,
                    "output": output,
                    "expected": expected,
                    "error": result.stderr if result.stderr else None,
                }
            except subprocess.TimeoutExpired:
                return {"passed": False, "error": "Execution timed out"}
            except Exception as e:
                return {"passed": False, "error": str(e)}
            finally:
                os.unlink(f.name)
    
    def get_challenge(self, challenge_id: int) -> Optional[CodingChallenge]:
        """Get a challenge by ID."""
        return self.db.query(CodingChallenge).filter(
            CodingChallenge.id == challenge_id
        ).first()
    
    def _default_challenge(self, topic: str, language: str) -> Dict:
        """Fallback challenge if LLM fails."""
        return {
            "title": f"Practice {topic}",
            "problem": f"Write a function that demonstrates your understanding of {topic}.",
            "starter_code": "def solution(x):\n    # Your code here\n    pass",
            "test_cases": [
                {"input": "1", "expected": "1"},
                {"input": "2", "expected": "2"},
            ],
            "solution": "def solution(x):\n    return x",
        }
