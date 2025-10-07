"""
Rerank Documents Use Case.

Application Layer - Clean Architecture

Use case atomique pour reranker des documents par pertinence.
Responsabilité unique: Affiner l'ordre des documents trouvés.
"""

from typing import Any, Dict, List

from app.application.commands import RerankDocumentsCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.services.reranker_service import IRerankerService
from app.infrastructure.observability.langfuse_decorator import trace_span


logger = get_logger(__name__)


class RerankDocumentsUseCase:
    """
    Use Case: Reranker des documents par pertinence.

    Responsabilité (SRP):
    - Affiner l'ordre des documents (Qdrant → Reranker)
    - Une seule raison de changer: si la logique de reranking change

    Flow:
    1. Convertir DTOs → dicts (format attendu par reranker)
    2. Appeler le service de reranking
    3. Convertir résultats → DTOs avec rerank_score
    4. Retourner top_k documents

    Pourquoi reranker?
    - Qdrant: Recherche rapide mais approximative (ANN)
    - Reranker: Modèle plus précis mais plus lent
    - Stratégie: Qdrant (top 10) → Reranker (top 5)

    Pourquoi ce use case?
    - Réutilisable: On peut reranker n'importe quelle liste de docs
    - Testable: Mock IRerankerService facilement
    - Découplé: Si on change de modèle de reranking, ce code ne change pas
    """

    def __init__(self, reranker_service: IRerankerService):
        """
        Injecte le service de reranking.

        Args:
            reranker_service: Service pour reranker documents (interface)
                             Ex: RerankerAdapter (avec jina-reranker-v2)
        """
        self.reranker_service = reranker_service

    async def execute(self, command: RerankDocumentsCommand) -> List[DocumentDTO]:
        """
        Exécute le reranking des documents (async).

        Args:
            command: Command contenant query, documents, top_k

        Returns:
            Liste de DocumentDTO avec rerank_score
            Triés par rerank_score (descendant)
            Limité à top_k documents

        Example:
            >>> # 10 documents de Qdrant
            >>> docs = await search_use_case.execute(...)
            >>> command = RerankDocumentsCommand(
            ...     query="Python FastAPI",
            ...     documents=docs,
            ...     top_k=5
            ... )
            >>> reranked = await use_case.execute(command)
            >>> print(len(reranked))  # 5 documents (les meilleurs)
            >>> print(reranked[0].rerank_score)  # Plus haut score
        """
        logger.info(
            "rerank_documents_use_case_started",
            input_count=len(command.documents),
            top_k=command.top_k,
        )

        # Cas spécial: aucun document à reranker
        if not command.documents:
            logger.warning("rerank_documents_no_input")
            return []

        # Étape 1: Convertir DTOs → dicts
        # Le reranker service attend un format dict spécifique
        docs_dicts: List[Dict[str, Any]] = [
            {
                "id": doc.id,
                "text": doc.text,
                "score": doc.score,
                "source": doc.source,
            }
            for doc in command.documents
        ]

        # Étape 2: Appeler le service de reranking (async)
        # Le service utilise HuggingFace API HTTP
        reranked_dicts = await self.reranker_service.rerank(
            query=command.query,
            documents=docs_dicts,
            top_k=command.top_k,
        )

        # Étape 3: Convertir résultats → DTOs
        # On ajoute le rerank_score aux DTOs
        reranked_documents = [
            DocumentDTO(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],  # Score Qdrant original
                source=doc["source"],
                rerank_score=doc.get("rerank_score"),  # Nouveau score du reranker
            )
            for doc in reranked_dicts
        ]

        logger.info(
            "rerank_documents_use_case_completed",
            output_count=len(reranked_documents),
        )

        return reranked_documents
