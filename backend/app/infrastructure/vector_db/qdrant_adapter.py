"""Qdrant adapter - implements IDocumentRepository."""

from typing import List, Dict, Any

from app.domain.repositories.document_repository import IDocumentRepository
from app.services.qdrant_service import QdrantService
from app.core.logging import get_logger

logger = get_logger(__name__)


class QdrantAdapter(IDocumentRepository):
    """
    Qdrant adapter implementing document repository interface.

    This is an Adapter in Hexagonal Architecture.
    It adapts Qdrant to the domain interface.
    """

    def __init__(self, qdrant_service: QdrantService) -> None:
        """
        Initialize adapter with Qdrant service.

        Args:
            qdrant_service: Qdrant service instance
        """
        self.qdrant_service = qdrant_service
        logger.info("qdrant_adapter_initialized")

    def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        return self.qdrant_service.search(
            query=query,
            limit=limit,
            score_threshold=score_threshold,
        )

    def upsert(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Upsert documents into repository."""
        self.qdrant_service.upsert_documents(
            documents=documents,
            metadatas=metadatas,
        )
