"""RAG Worker API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from shared.observability import RequestIdMiddleware, setup_logging, get_logger
from shared.db import get_session
from app.core.config import settings
from app.services import RetrievalService


setup_logging(level=settings.LOG_LEVEL, json_format=False, service_name="rag-worker")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RAG Worker service starting", port=settings.RAG_WORKER_PORT)
    yield
    logger.info("RAG Worker service shutting down")


app = FastAPI(
    title="Learning Resolution Coach - RAG Worker",
    description="Retrieval and citation service",
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
class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5
    topic: Optional[str] = None
    checkin_id: Optional[int] = None


class RetrieveResponse(BaseModel):
    results: List[dict]
    citations: List[dict]


class IngestRequest(BaseModel):
    title: str
    url: str
    content: str
    topic: str
    resource_type: Optional[str] = None
    difficulty: Optional[str] = None


class ResourceResponse(BaseModel):
    id: int
    title: str
    url: str
    topic: str
    resource_type: Optional[str]
    difficulty: Optional[str]


# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-worker"}


@app.post("/v1/retrieve", response_model=RetrieveResponse)
async def retrieve(
    request: RetrieveRequest,
    db: Session = Depends(get_session),
):
    """Retrieve relevant resources for a query."""
    service = RetrievalService(db)
    return await service.retrieve(
        query=request.query,
        top_k=request.top_k,
        topic=request.topic,
        checkin_id=request.checkin_id,
    )


@app.get("/v1/resources")
async def list_resources(
    topic: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    """List available resources."""
    service = RetrievalService(db)
    resources = service.get_resources(topic=topic, limit=limit)
    
    return {
        "resources": [
            {
                "id": r.id,
                "title": r.title,
                "url": r.url,
                "topic": r.topic,
                "resource_type": r.resource_type,
                "difficulty": r.difficulty,
            }
            for r in resources
        ]
    }


@app.post("/v1/resources/ingest", response_model=ResourceResponse)
async def ingest_resource(
    request: IngestRequest,
    db: Session = Depends(get_session),
):
    """Ingest a new resource into the vector store."""
    service = RetrievalService(db)
    resource = await service.ingest_resource(
        title=request.title,
        url=request.url,
        content=request.content,
        topic=request.topic,
        resource_type=request.resource_type,
        difficulty=request.difficulty,
    )
    
    return ResourceResponse(
        id=resource.id,
        title=resource.title,
        url=resource.url,
        topic=resource.topic,
        resource_type=resource.resource_type,
        difficulty=resource.difficulty,
    )


@app.get("/v1/stats")
async def get_stats(
    db: Session = Depends(get_session),
):
    """Get RAG system statistics."""
    service = RetrievalService(db)
    
    from shared.db.models import Resource, RetrievalLog
    
    resource_count = db.query(Resource).count()
    retrieval_count = db.query(RetrievalLog).count()
    vector_count = await service.get_vector_store_count()
    
    return {
        "resources_in_db": resource_count,
        "documents_in_vector_store": vector_count,
        "total_retrievals": retrieval_count,
    }
