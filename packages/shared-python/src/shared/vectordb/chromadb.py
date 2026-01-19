"""ChromaDB vector store implementation."""

import uuid
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from shared.vectordb.base import VectorStore, SearchResult


class ChromaDBStore(VectorStore):
    """ChromaDB vector store (local development, in-memory or persistent)."""

    def __init__(
        self,
        collection_name: str = "learning_resources",
        persist_directory: Optional[str] = None,
    ):
        """Initialize ChromaDB store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data (in-memory if None)
        """
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            self.client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False),
            )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def store_name(self) -> str:
        return "chromadb"

    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        
        return ids

    async def add_embeddings(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        
        return ids

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> List[SearchResult]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances, convert to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1.0 - distance  # Cosine distance to similarity
                
                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    score=score,
                ))
        
        return search_results

    async def search_by_embedding(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> List[SearchResult]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1.0 - distance
                
                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    score=score,
                ))
        
        return search_results

    async def delete(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids)

    async def get(self, ids: List[str]) -> List[dict]:
        results = self.collection.get(
            ids=ids,
            include=["documents", "metadatas"],
        )
        
        docs = []
        if results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                docs.append({
                    "id": doc_id,
                    "content": results["documents"][i] if results["documents"] else "",
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                })
        
        return docs

    async def count(self) -> int:
        return self.collection.count()
