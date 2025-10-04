"""Embedding service using HuggingFace models."""

from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self) -> None:
        """Initialize the embedding model."""
        logger.info("loading_embedding_model", model=settings.embedding_model)
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info("embedding_model_loaded", model=settings.embedding_model)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
