"""
Vector Database Adapters.

Infrastructure Layer - Clean Architecture

Adapters pour les bases de données vectorielles et embeddings.
"""

from app.infrastructure.vector_db.embedding_adapter import MultilingualEmbeddingAdapter
from app.infrastructure.vector_db.qdrant_adapter import QdrantAdapter

__all__ = ["QdrantAdapter", "MultilingualEmbeddingAdapter"]
