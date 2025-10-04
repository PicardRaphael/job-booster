"""Repository interfaces - Dependency Inversion."""

from app.domain.repositories.document_repository import IDocumentRepository
from app.domain.repositories.llm_provider import ILLMProvider

__all__ = ["IDocumentRepository", "ILLMProvider"]
