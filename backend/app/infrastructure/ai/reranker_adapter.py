"""Reranker adapter - implements IRerankerService via HuggingFace API HTTP."""

from typing import List, Dict, Any
import asyncio
import inspect

from app.domain.services.reranker_service import IRerankerService
from app.services.local_reranker import get_local_reranker_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class RerankerAdapter(IRerankerService):
    """
    Reranker adapter implementing domain service interface.

    Adapts HuggingFace Reranker Service (HTTP API) to domain interface.

    Pattern Adapter (Hexagonal Architecture):
    - Adapte le service reranker HuggingFace à l'interface domain
    - Permet de changer de modèle facilement via API HTTP
    - Isole le domain des détails d'implémentation

    Modèles supportés:
    - BAAI/bge-reranker-base
    - BAAI/bge-reranker-v2-m3
    - cross-encoder/ms-marco-MiniLM-L-6-v2

    Example:
        >>> adapter = RerankerAdapter()
        >>> docs = [{"text": "Python dev"}, {"text": "Java dev"}]
        >>> reranked = await adapter.rerank("Python", docs, top_k=1)
        >>> print(reranked[0]["rerank_score"])
        0.95
    """

    def __init__(self) -> None:
        """
        Initialize adapter with HuggingFace reranker service.

        Uses get_local_reranker_service() singleton.
        """
        self.reranker_service = get_local_reranker_service()
        logger.info("reranker_adapter_initialized")

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Rerank documents by relevance via selected provider.

        Supports both async and sync implementations of the underlying service.
        """
        if inspect.iscoroutinefunction(self.reranker_service.rerank):
            return await self.reranker_service.rerank(
                query=query,
                documents=documents,
                top_k=top_k,
            )

        # If the impl is synchronous, offload to a worker thread
        return await asyncio.to_thread(self.reranker_service.rerank, query, documents, top_k)
