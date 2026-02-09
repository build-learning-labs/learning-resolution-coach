"""Retrieval service for RAG Worker."""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import hashlib

from shared.vectordb.chromadb import ChromaDBStore
from shared.vectordb.base import VectorStore, SearchResult
from shared.db.models import Resource, RetrievalLog
from shared.observability import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RetrievalService:
    """Service for retrieving relevant resources with enhanced RAG capabilities."""
    
    def __init__(self, db: Session, vector_store: Optional[VectorStore] = None):
        self.db = db
        self.vector_store = vector_store or self._create_vector_store()
    
    def _create_vector_store(self) -> VectorStore:
        """Create vector store based on configuration."""
        if settings.VECTOR_STORE == "chromadb":
            return ChromaDBStore(
                collection_name=settings.CHROMA_COLLECTION,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
        return ChromaDBStore(collection_name=settings.CHROMA_COLLECTION)

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better embedding accuracy."""
        if not text:
            return []
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None, # Added difficulty filter
        checkin_id: Optional[int] = None,
    ) -> Dict:
        """Retrieve relevant resources for a query."""
        logger.info("Retrieving resources", query=query[:50], top_k=top_k)
        
        # Build filters
        filters = {}
        if topic:
            filters["topic"] = topic
        if difficulty:
            filters["difficulty"] = difficulty
            
        # Handle empty filters for ChromaDB (it expects None if empty)
        if not filters:
            filters = None
        
        # Search vector store
        try:
            results = await self.vector_store.search(
                query=query,
                top_k=top_k,
                filters=filters,
            )
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            results = []
        
        # Format results
        formatted_results = []
        citations = []
        
        for result in results:
            formatted_results.append({
                "id": result.id,
                "content": result.content,  # FIX: Removed [:500] limit
                "score": result.score,
                "metadata": result.metadata,
            })
            
            # Build citation
            if result.metadata:
                citations.append({
                    "title": result.metadata.get("title", "Resource"),
                    "url": result.metadata.get("url", ""),
                    "relevance": result.score,
                })
        
        # Log retrieval
        log = RetrievalLog(
            checkin_id=checkin_id,
            query=query,
            hits_json={"results": [r["id"] for r in formatted_results]},
            citations={"citations": citations},
        )
        self.db.add(log)
        self.db.commit()
        
        return {
            "results": formatted_results,
            "citations": citations,
        }
    
    async def ingest_resource(
        self,
        title: str,
        url: str,
        content: str,
        topic: str,
        resource_type: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Resource:
        """Ingest a new resource into the system with chunking."""
        logger.info("Ingesting resource", title=title, topic=topic)
        
        # Create content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if resource already exists
        existing = self.db.query(Resource).filter(
            Resource.content_hash == content_hash
        ).first()
        
        if existing:
            logger.info("Resource already exists", id=existing.id)
            return existing
        
        # Create resource record (SQL)
        resource = Resource(
            title=title,
            url=url,
            topic=topic,
            content=content,
            content_hash=content_hash,
            resource_type=resource_type,
            difficulty=difficulty,
        )
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        
        # Chunking Logic
        chunks = self._split_text(content)
        chunk_metadatas = []
        chunk_ids = []
        
        for i, _ in enumerate(chunks):
            # Metadata for each chunk
            chunk_metadatas.append({
                "title": title,
                "url": url,
                "topic": topic,
                "resource_type": resource_type or "",
                "difficulty": difficulty or "",
                "resource_id": str(resource.id),
                "chunk_index": i
            })
            chunk_ids.append(f"{resource.id}_{i}")

        # Add chunks to vector store
        try:
            await self.vector_store.add_documents(
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids,
            )
        except Exception as e:
            logger.error("Failed to add to vector store", error=str(e))
        
        return resource
    
    def get_resources(
        self,
        topic: Optional[str] = None,
        limit: int = 20,
    ) -> List[Resource]:
        """Get resources, optionally filtered by topic."""
        query = self.db.query(Resource)
        if topic:
            query = query.filter(Resource.topic == topic)
        return query.limit(limit).all()
    
    async def get_vector_store_count(self) -> int:
        """Get count of documents in vector store."""
        try:
            return await self.vector_store.count()
        except Exception:
            return 0