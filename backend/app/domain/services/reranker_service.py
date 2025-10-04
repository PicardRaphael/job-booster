"""Reranker service interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IRerankerService(ABC):
    """
    Interface for document reranking service.

    Implémentations possibles:
    - RerankerAdapter (actuel avec HuggingFace API HTTP)
    - OpenAIRerankerAdapter (avec OpenAI rerank API)
    - LocalRerankerAdapter (avec cross-encoder en local)
    """

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents by relevance (async).

        Args:
            query: Search query
            documents: List of candidate documents (must have "text" key)
            top_k: Number of top results to return

        Returns:
            Reranked documents with "rerank_score" added

        Note:
            Méthode async car utilise l'API HTTP HuggingFace

        Example:
            >>> docs = [{"text": "Python"}, {"text": "Java"}]
            >>> reranked = await reranker.rerank("Python dev", docs, top_k=1)
            >>> print(reranked[0]["rerank_score"])
            0.95
        """
        pass
