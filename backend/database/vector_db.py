"""Chroma vector database integration for Academian Platform"""

import chromadb
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Initialize Chroma client
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

chroma_db_path = data_dir / "chroma_db"
chroma_db_path.mkdir(exist_ok=True)

# Initialize Chroma client with persistent storage (new API)
chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))

# Lazy-load sentence transformer for embeddings (loaded on first use)
_embedding_model = None

def get_embedding_model():
    """Get or initialize the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")
    return _embedding_model


class ChromaVectorStore:
    """Wrapper for Chroma vector database operations"""

    def __init__(self, collection_name: str = "academian_content"):
        """Initialize vector store with a specific collection"""
        self.collection_name = collection_name
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name
        )
        logger.info(f"Initialized Chroma collection: {collection_name}")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            metadatas: List of metadata dicts for each document
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        import uuid

        embeddings = get_embedding_model().encode(documents)

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Added {len(documents)} documents to {self.collection_name}")
        return ids

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents

        Args:
            query: Query text
            n_results: Number of results to return
            where: Optional filter conditions

        Returns:
            Dict with ids, distances, metadatas, and documents
        """
        query_embedding = embedding_model.encode([query])

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where
        )

        return results

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store"""
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from {self.collection_name}")

    def update_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Update documents in the vector store"""
        embeddings = get_embedding_model().encode(documents)

        self.collection.update(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        logger.info(f"Updated {len(ids)} documents in {self.collection_name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            "collection_name": self.collection_name,
            "count": self.collection.count()
        }


# Pre-initialized collections for different domains
content_vector_store = ChromaVectorStore("academian_content")
knowledge_vector_store = ChromaVectorStore("academian_knowledge")
skills_vector_store = ChromaVectorStore("academian_skills")
standards_vector_store = ChromaVectorStore("academian_standards")


def get_vector_store(collection_name: str = "academian_content") -> ChromaVectorStore:
    """Get or create a vector store for a specific collection"""
    if collection_name == "academian_content":
        return content_vector_store
    elif collection_name == "academian_knowledge":
        return knowledge_vector_store
    elif collection_name == "academian_skills":
        return skills_vector_store
    elif collection_name == "academian_standards":
        return standards_vector_store
    else:
        return ChromaVectorStore(collection_name)


def persist_chroma_db():
    """Persist Chroma database to disk"""
    # PersistentClient automatically persists data
    logger.info("Chroma database is using persistent storage")
