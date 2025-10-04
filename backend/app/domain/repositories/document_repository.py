"""Document repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDocumentRepository(ABC):
    """
    Interface for document storage and retrieval.

    This is a Port in Hexagonal Architecture.
    Implementations are Adapters.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents (async).

        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of matching documents with metadata

        Note:
            Async car utilise embeddings via HuggingFace API HTTP
        """
        pass

    @abstractmethod
    async def upsert(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Upsert documents into repository (async).

        Args:
            documents: List of document texts
            metadatas: List of document metadata

        Note:
            Async car utilise embeddings via HuggingFace API HTTP
        """
        pass
