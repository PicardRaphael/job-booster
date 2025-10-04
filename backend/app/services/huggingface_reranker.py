"""HuggingFace Reranker service using HTTP API."""

import httpx
from typing import Any, Dict, List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HuggingFaceRerankerService:
    """Service for reranking search results via HuggingFace Inference API."""

    API_URL = "https://api-inference.huggingface.co/models"

    def __init__(self) -> None:
        """Initialize the HuggingFace reranker service."""
        self.model = settings.reranker_model
        self.api_key = settings.huggingface_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.endpoint = f"{self.API_URL}/{self.model}"
        logger.info("huggingface_reranker_service_initialized", model=self.model)

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance via HuggingFace API."""
        if not documents:
            return []

        logger.info("reranking_documents_via_hf_api", query=query[:100], count=len(documents))

        # Extract text from documents
        texts = [doc["text"] for doc in documents]

        # Call HuggingFace reranker API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.endpoint,
                headers=self.headers,
                json={
                    "inputs": {
                        "source_sentence": query,
                        "sentences": texts,
                    },
                    "options": {"wait_for_model": True},
                },
            )
            response.raise_for_status()
            scores = response.json()

        # Add rerank scores to documents
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        # Sort by rerank score (descending)
        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        # Limit results if top_k specified
        if top_k:
            reranked = reranked[:top_k]

        logger.info("reranking_completed_via_hf_api", results_count=len(reranked))
        return reranked


# Singleton instance
_hf_reranker_service: HuggingFaceRerankerService | None = None


def get_hf_reranker_service() -> HuggingFaceRerankerService:
    """Get or create the singleton HuggingFace reranker service."""
    global _hf_reranker_service
    if _hf_reranker_service is None:
        _hf_reranker_service = HuggingFaceRerankerService()
    return _hf_reranker_service
