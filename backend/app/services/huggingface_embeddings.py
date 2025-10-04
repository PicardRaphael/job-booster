"""HuggingFace Embedding service using HTTP API."""

import httpx
from typing import List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HuggingFaceEmbeddingService:
    """Service for generating text embeddings via HuggingFace Inference API."""

    API_URL = "https://api-inference.huggingface.co/models"

    def __init__(self) -> None:
        """Initialize the HuggingFace embedding service."""
        self.model = settings.embedding_model
        self.api_key = settings.huggingface_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.endpoint = f"{self.API_URL}/{self.model}"
        logger.info("huggingface_embedding_service_initialized", model=self.model)

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts via HuggingFace API."""
        logger.info("embedding_texts_via_hf_api", count=len(texts), model=self.model)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.endpoint,
                headers=self.headers,
                json={"inputs": texts},
            )

            # Log error details before raising
            if response.status_code != 200:
                error_detail = response.text
                logger.error("hf_api_error", status=response.status_code, detail=error_detail)

            response.raise_for_status()
            embeddings = response.json()

        logger.info(
            "texts_embedded_via_hf_api",
            count=len(embeddings),
            dimension=len(embeddings[0]) if embeddings else 0,
        )
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Synchronous wrapper for embed_text.
        Note: For async contexts, use embed_text directly.
        """
        import asyncio

        try:
            # Try to get the running event loop
            loop = asyncio.get_running_loop()
            # If we're already in an async context, we can't use asyncio.run
            raise RuntimeError(
                "Cannot use embed_query in async context. Use await embed_text() instead."
            )
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(self.embed_text(query))

    def get_dimension(self) -> int:
        """
        Get the embedding dimension based on the model.

        Common HuggingFace model dimensions:
        - intfloat/multilingual-e5-base: 768
        - intfloat/multilingual-e5-large: 1024
        - sentence-transformers/all-MiniLM-L6-v2: 384
        - BAAI/bge-large-en-v1.5: 1024
        - BAAI/bge-base-en-v1.5: 768
        """
        dimension_map = {
            "intfloat/multilingual-e5-base": 768,
            "intfloat/multilingual-e5-large": 1024,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "BAAI/bge-large-en-v1.5": 1024,
            "BAAI/bge-base-en-v1.5": 768,
        }

        dimension = dimension_map.get(self.model, 768)  # Default to 768
        logger.info("embedding_dimension_retrieved", model=self.model, dimension=dimension)
        return dimension


# Singleton instance
_hf_embedding_service: HuggingFaceEmbeddingService | None = None


def get_hf_embedding_service() -> HuggingFaceEmbeddingService:
    """Get or create the singleton HuggingFace embedding service."""
    global _hf_embedding_service
    if _hf_embedding_service is None:
        _hf_embedding_service = HuggingFaceEmbeddingService()
    return _hf_embedding_service
