"""Seed data script for Holistic AI Strategy Resources."""

import httpx
import json

# Configuration
RAG_WORKER_URL = "http://localhost:8002"
EVALUATOR_URL = "http://localhost:8003"

def seed_evaluation_dataset():
    print("🌱 Seeding Holistic AI Strategy Resources...")  # REMOVED: Ikigai
    
    resources = [
        # ==========================================
        # TECHNICAL TRACKS
        # ==========================================
        
        # 1. Agentic Design (LangGraph & CrewAI)
        {
            "title": "Architecting Autonomous Agents with LangGraph",
            "url": "https://langchain-ai.github.io/langgraph/",
            "content": "LangGraph enables the creation of stateful, multi-actor agents. Unlike linear chains, it supports cycles (loops), which are essential for advanced autonomous behaviors like reflection, self-correction, and iterative planning. Key concept: Nodes, Edges, and Shared State.",
            "topic": "tech_agentic",
            "resource_type": "documentation",
            "difficulty": "advanced"
        },
        {
            "title": "CrewAI: Orchestrating Role-Playing Agents",
            "url": "https://www.crewai.com/",
            "content": "CrewAI focuses on role-based agent orchestration. You define specific roles (e.g., 'Researcher', 'Writer') and goals. The framework handles the delegation and collaboration between these agents to accomplish complex tasks automonously.",
            "topic": "tech_agentic",
            "resource_type": "guide",
            "difficulty": "intermediate"
        },

        # 2. Edge AI (Privacy & Efficiency)
        {
            "title": "Local LLMs with Ollama",
            "url": "https://ollama.com/",
            "content": "Ollama is the standard for running LLMs locally on Linux/macOS. It abstracts the complexity of model weights (GGUF) and provides a simple API. Essential for building privacy-preserving apps that do not send user data to OpenAI.",
            "topic": "tech_edge",
            "resource_type": "tool_guide",
            "difficulty": "beginner"
        },
        {
            "title": "Apple MLX: Deep Learning on Silicon",
            "url": "https://github.com/ml-explore/mlx",
            "content": "MLX is a NumPy-like array framework designed for efficiency on Apple Silicon. It allows for unified memory access, enabling training and inference of large models (like Llama 3 8B) directly on a MacBook Air.",
            "topic": "tech_edge",
            "resource_type": "repository",
            "difficulty": "advanced"
        },

        # 3. AI Evals (Red Teaming)
        {
            "title": "Ragas: Evaluation Metrics for RAG",
            "url": "https://docs.ragas.io/",
            "content": "Ragas offers a suite of metrics to evaluate RAG pipelines: Faithfulness (did the AI make it up?), Answer Relevance (did it answer the user?), and Context Precision. It uses an 'LLM-as-a-Judge' approach to automate quality assurance.",
            "topic": "tech_evals",
            "resource_type": "documentation",
            "difficulty": "advanced"
        },

        # ==========================================
        # HUMAN TRACKS
        # ==========================================

        # 4. AI Ethics & Governance
        {
            "title": "NIST AI Risk Management Framework (AI RMF)",
            "url": "https://www.nist.gov/itl/ai-risk-management-framework",
            "content": "The US Government's standard for managing AI risk. It breaks governance into four functions: Govern, Map, Measure, and Manage. Essential knowledge for working in Fintech, Healthcare, or Government AI roles.",
            "topic": "non_tech_ethics",
            "resource_type": "framework",
            "difficulty": "intermediate"
        },

        # 5. AI Product Management
        {
            "title": "Google PAIR: People + AI Guidebook",
            "url": "https://pair.withgoogle.com/",
            "content": "A comprehensive guide to designing human-centric AI products. Covers 'Mental Models' (how users think AI works vs how it actually works), 'Trust Calibration', and 'Explainability'. Focuses on augmentation over automation.",
            "topic": "non_tech_product",
            "resource_type": "guide",
            "difficulty": "beginner"
        },

        # 6. Cognitive Resilience
        {
            "title": "Deep Work: Rules for Focused Success",
            "url": "https://www.calnewport.com/books/deep-work/",
            "content": "In the AI age, 'shallow work' (emails, meetings) will be automated. 'Deep Work' (cognitively demanding tasks performed without distraction) is the only skill that remains valuable. This resource teaches strategies to rebuild your attention span.",
            "topic": "non_tech_mind",
            "resource_type": "book_summary",
            "difficulty": "beginner"
        }
    ]
    
    print(f"Creating {len(resources)} resources...")
    for res in resources:
        try:
            httpx.post(f"{RAG_WORKER_URL}/v1/resources/ingest", json=res, timeout=10.0)
            print(f"  - Ingested: {res['title']}")
        except Exception as e:
            print(f"  - Failed to ingest {res['title']}: {e}")

    print("Holistic Strategy Seeding Complete!") # REMOVED: Ikigai

if __name__ == "__main__":
    seed_evaluation_dataset()