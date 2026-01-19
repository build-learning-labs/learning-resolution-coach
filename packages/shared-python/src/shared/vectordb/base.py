"""Abstract vector store interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from pydantic import BaseModel


class SearchResult(BaseModel):
    """Result from vector similarity search."""
    
    id: str
    content: str
    metadata: dict = {}
    score: float = 0.0


class VectorStore(ABC):
    """Abstract interface for all vector database providers.
    
    Implementations:
    - ChromaDBStore (local dev, in-memory or persistent)
    - PineconeStore (cloud, managed)
    - QdrantStore (self-hosted or cloud)
    - PgVectorStore (PostgreSQL extension)
    """

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Name of the vector store."""
        ...

    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            documents: List of text documents to add
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document (generated if not provided)
            
        Returns:
            List of document IDs
        """
        ...

    @abstractmethod
    async def add_embeddings(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add pre-computed embeddings to the vector store.
        
        Args:
            embeddings: Pre-computed embedding vectors
            documents: Original text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document
            
        Returns:
            List of document IDs
        """
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> List[SearchResult]:
        """Search for similar documents using text query.
        
        Args:
            query: Text query to search for
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        ...

    @abstractmethod
    async def search_by_embedding(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> List[SearchResult]:
        """Search for similar documents using embedding vector.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        ...

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by ID.
        
        Args:
            ids: List of document IDs to delete
        """
        ...

    @abstractmethod
    async def get(self, ids: List[str]) -> List[dict]:
        """Get documents by ID.
        
        Args:
            ids: List of document IDs to retrieve
            
        Returns:
            List of document data
        """
        ...

    async def count(self) -> int:
        """Get total number of documents in the store.
        
        Returns:
            Document count
        """
        raise NotImplementedError("count() not implemented for this store")
