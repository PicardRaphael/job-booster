"""Reranker adapter - implements IRerankerService."""

from typing import List, Dict, Any

from app.domain.services.reranker_service import IRerankerService
from app.services.reranker import RerankerService
from app.core.logging import get_logger

logger = get_logger(__name__)


class RerankerAdapter(IRerankerService):
    """
    Reranker adapter implementing domain service interface.

    Adapts RerankerService to domain interface.
    """

    def __init__(self, reranker_service: RerankerService) -> None:
        """
        Initialize adapter with reranker service.

        Args:
            reranker_service: Reranker service instance
        """
        self.reranker_service = reranker_service
        logger.info("reranker_adapter_initialized")

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Rerank documents by relevance."""
        return self.reranker_service.rerank(
            query=query,
            documents=documents,
            top_k=top_k,
        )
