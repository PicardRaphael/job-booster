"""Qdrant vector database service."""

from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.core.logging import get_logger
from app.services.embeddings import get_embedding_service

logger = get_logger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        logger.info("connecting_to_qdrant", url=settings.qdrant_url)
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection
        self.embedding_service = get_embedding_service()
        logger.info("qdrant_connected", collection=self.collection_name)

    def ensure_collection(self, recreate: bool = False) -> None:
        """Ensure the collection exists, create if not."""
        vector_size = self.embedding_service.get_dimension()

        if recreate and self.client.collection_exists(self.collection_name):
            logger.warning("deleting_existing_collection", collection=self.collection_name)
            self.client.delete_collection(self.collection_name)

        if not self.client.collection_exists(self.collection_name):
            logger.info("creating_collection", collection=self.collection_name, dimension=vector_size)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("collection_created", collection=self.collection_name)
        else:
            logger.info("collection_exists", collection=self.collection_name)

    def upsert_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str] | None = None,
    ) -> None:
        """Upsert documents into the collection."""
        logger.info("upserting_documents", count=len(documents))

        embeddings = self.embedding_service.embed_texts(documents)

        if ids is None:
            # Use integers as IDs (Qdrant requirement)
            ids = list(range(len(documents)))

        points = [
            PointStruct(
                id=int(id_) if isinstance(id_, str) else id_,  # Ensure integer ID
                vector=embedding,
                payload={
                    "text": doc,
                    **metadata,
                },
            )
            for id_, doc, embedding, metadata in zip(ids, documents, embeddings, metadatas)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info("documents_upserted", count=len(documents))

    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        logger.info("searching_documents", query=query[:100], limit=limit)

        query_vector = self.embedding_service.embed_text(query)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        documents = [
            {
                "id": str(result.id),
                "text": result.payload.get("text", ""),
                "score": result.score,
                "source": result.payload.get("source", ""),
                "metadata": result.payload,
            }
            for result in results
        ]

        logger.info("search_completed", results_count=len(documents))
        return documents


# Singleton instance
_qdrant_service: QdrantService | None = None


def get_qdrant_service() -> QdrantService:
    """Get or create the singleton Qdrant service."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
