"""Reranking service using HuggingFace cross-encoder models."""

from typing import Any, Dict, List

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RerankerService:
    """Service for reranking search results."""

    def __init__(self) -> None:
        """Initialize the reranker model."""
        logger.info("loading_reranker_model", model=settings.reranker_model)
        self.model = CrossEncoder(settings.reranker_model)
        logger.info("reranker_model_loaded", model=settings.reranker_model)

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance."""
        if not documents:
            return []

        logger.info("reranking_documents", query=query[:100], count=len(documents))

        # Prepare pairs for cross-encoder
        pairs = [[query, doc["text"]] for doc in documents]

        # Get reranking scores
        scores = self.model.predict(pairs)

        # Add rerank scores to documents
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        # Sort by rerank score
        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        # Limit results if top_k specified
        if top_k:
            reranked = reranked[:top_k]

        logger.info("reranking_completed", results_count=len(reranked))
        return reranked


# Singleton instance
_reranker_service: RerankerService | None = None


def get_reranker_service() -> RerankerService:
    """Get or create the singleton reranker service."""
    global _reranker_service
    if _reranker_service is None:
        _reranker_service = RerankerService()
    return _reranker_service
