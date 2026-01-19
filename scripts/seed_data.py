"""Seed data script for evaluation dataset."""

import httpx

import json
from datetime import date, timedelta

# Configuration
GATEWAY_URL = "http://localhost:8000"
CORE_AGENT_URL = "http://localhost:8001"
RAG_WORKER_URL = "http://localhost:8002"
EVALUATOR_URL = "http://localhost:8003"


def seed_evaluation_dataset():
    """Create initial dataset for evaluation."""
    print("🌱 Seeding evaluation dataset...")
    
    # 1. Create resources in RAG Worker
    resources = [
        {
            "title": "Python Basics - Variables and Types",
            "url": "https://docs.python.org/3/tutorial/introduction.html",
            "content": "Python is a dynamically typed language. Variables do not need to be declared with any particular type, and can even change type after they have been set. Python supports integers, floating point numbers, and complex numbers.",
            "topic": "python_basics",
            "resource_type": "documentation",
            "difficulty": "beginner"
        },
        {
            "title": "Python Control Flow",
            "url": "https://docs.python.org/3/tutorial/controlflow.html",
            "content": "The if statement is used for conditional execution. Python uses indentation to group statements. The for statement iterates over the items of any sequence (a list or a string), in the order that they appear in the sequence.",
            "topic": "python_control_flow",
            "resource_type": "documentation",
            "difficulty": "beginner"
        },
        {
            "title": "Clean Code Principles",
            "url": "https://example.com/clean-code",
            "content": "Clean code is readable and maintainable. Functions should do one thing and do it well. Variable names should be descriptive. Comments should explain why, not what.",
            "topic": "software_engineering",
            "resource_type": "article",
            "difficulty": "intermediate"
        }
    ]
    
    print(f"Creating {len(resources)} resources...")
    for res in resources:
        try:
            # Direct call to RAG worker using httpx
            httpx.post(f"{RAG_WORKER_URL}/v1/resources/ingest", json=res)
            print(f"  - Ingested: {res['title']}")
        except Exception as e:
            print(f"  - Failed to ingest {res['title']}: {e}")
            
    # 2. Create Coding Challenges
    challenges = [
        {
            "topic": "Python Lists",
            "difficulty": "easy",
            "language": "python"
        },
        {
            "topic": "String Manipulation",
            "difficulty": "medium",
            "language": "python"
        }
    ]
    
    print(f"Generating {len(challenges)} coding challenges...")
    for chal in challenges:
        try:
            httpx.post(f"{EVALUATOR_URL}/v1/coding/generate", json=chal, headers={"x-user-id": "1"})
            print(f"  - Generated challenge for {chal['topic']}")
        except Exception as e:
            print(f"  - Failed to generate challenge: {e}")

    print("✅ Seeding complete!")


if __name__ == "__main__":
    seed_evaluation_dataset()
