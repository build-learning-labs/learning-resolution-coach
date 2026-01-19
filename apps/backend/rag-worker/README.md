# 📚 RAG Worker

The semantic engine that provides the AI with "memory" via Retrieval Augmented Generation.

## 🚀 Role
- **Ingestion**: Processes PDFs/Markdown and stores vectorized embeddings.
- **Retrieval**: Performs semantic search across the knowledge corpus.
- **Endpoint**: [http://localhost:8002](http://localhost:8002)

## 🛠️ Tech Stack
- ChromaDB (Vector Store)
- FastAPI
- Embeddings (OpenAI / Local)
