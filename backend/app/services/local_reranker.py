"""Local reranker service using FlagEmbedding."""

from typing import Any, Dict, List
from FlagEmbedding import FlagReranker
from app.core.logging import get_logger

logger = get_logger(__name__)


class LocalRerankerService:
    """Service for reranking documents locally using BAAI/bge-reranker-v2-m3."""

    def __init__(self) -> None:
        self.model_name = "BAAI/bge-reranker-v2-m3"
        logger.info("loading_local_reranker_model", model=self.model_name)
        self.reranker = FlagReranker(self.model_name, use_fp16=False)
        logger.info("local_reranker_loaded")

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Rerank documents locally without external API."""
        if not documents:
            return []

        logger.info("reranking_documents_locally", query=query[:100], count=len(documents))

        pairs = [[query, doc["text"]] for doc in documents]
        scores = self.reranker.compute_score(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        if top_k:
            reranked = reranked[:top_k]

        logger.info("reranking_completed_locally", results_count=len(reranked))
        return reranked


# Singleton
_local_reranker_service: LocalRerankerService | None = None


def get_local_reranker_service() -> LocalRerankerService:
    global _local_reranker_service
    if _local_reranker_service is None:
        _local_reranker_service = LocalRerankerService()
    return _local_reranker_service
