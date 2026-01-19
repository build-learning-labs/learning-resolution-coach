# 📦 Shared Python Package (`shared`)

The core library containing common utilities, database models, and AI engine adapters used by all backend microservices.

## 🏗️ Structure
- **`db`**: SQLAlchemy models and session management.
- **`llm`**: Unified adapters for OpenAI, Anthropic, and Ollama.
- **`schemas`**: Core Pydantic V2 data contracts.
- **`observability`**: Opik tracing and structured logging (Structlog).

## 🚀 Installation

```bash
# Standard install (editable mode)
pip install -e .

# With specific vector store support
pip install -e ".[ollama]"
pip install -e ".[pinecone]"

# Development tools (Pytest, Ruff, Black)
pip install -e ".[dev]"
```

## 🔍 Observability
Tracing is disabled by default. Set `OPIK_API_KEY` in your environment to enable automatic trace capture across all services using this package.
