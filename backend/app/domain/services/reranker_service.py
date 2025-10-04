"""Reranker service interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IRerankerService(ABC):
    """Interface for document reranking service."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents by relevance.

        Args:
            query: Search query
            documents: List of candidate documents
            top_k: Number of top results to return

        Returns:
            Reranked documents
        """
        pass
