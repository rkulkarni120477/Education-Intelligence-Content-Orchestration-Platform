import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
from config import get_settings
import json
from database.models import ContentEmbedding
from sqlalchemy.orm import Session

settings = get_settings()


class EmbeddingManager:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text chunk"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text chunks"""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

    def search_similar(self, query_embedding: List[float], embeddings: List[List[float]], top_k: int = 5) -> List[Tuple[int, float]]:
        """Find top-k most similar embeddings"""
        similarities = []
        for idx, embedding in enumerate(embeddings):
            sim = self.similarity(query_embedding, embedding)
            similarities.append((idx, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def store_embedding(self, db: Session, content_id: str, chunk_index: int, text_chunk: str, embedding: List[float]):
        """Store embedding in database"""
        db_embedding = ContentEmbedding(
            content_id=content_id,
            chunk_index=chunk_index,
            text_chunk=text_chunk,
            embedding=embedding,
            embedding_model=settings.EMBEDDING_MODEL
        )
        db.add(db_embedding)
        db.commit()

    def retrieve_embeddings(self, db: Session, content_id: str) -> List[ContentEmbedding]:
        """Retrieve embeddings for content"""
        return db.query(ContentEmbedding).filter(ContentEmbedding.content_id == content_id).all()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    if not text:
        return chunks

    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap

    return chunks
