"""
Search Documents Use Case.

Application Layer - Clean Architecture

Use case atomique pour chercher des documents dans la base vectorielle.
Responsabilité unique: Recherche sémantique dans Qdrant.
"""

from typing import List

from app.application.commands import SearchDocumentsCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.repositories.document_repository import IDocumentRepository

logger = get_logger(__name__)


class SearchDocumentsUseCase:
    """
    Use Case: Chercher des documents dans la base vectorielle.

    Responsabilité (SRP):
    - Recherche sémantique dans Qdrant
    - Une seule raison de changer: si la logique de recherche change

    Flow:
    1. Appeler le repository avec la query
    2. Convertir résultats dicts → DTOs
    3. Retourner liste de DocumentDTOs

    Pourquoi ce use case?
    - Réutilisable: On peut chercher sans analyser ni générer
    - Testable: Mock IDocumentRepository facilement
    - Découplé: Si on change Qdrant pour Pinecone, ce code ne change pas
    """

    def __init__(self, document_repository: IDocumentRepository):
        """
        Injecte le repository de documents.

        Args:
            document_repository: Repository pour chercher documents (interface)
                                Ex: QdrantAdapter, PineconeAdapter
        """
        self.document_repository = document_repository

    def execute(self, command: SearchDocumentsCommand) -> List[DocumentDTO]:
        """
        Exécute la recherche de documents.

        Args:
            command: Command contenant query, limit, score_threshold

        Returns:
            Liste de DocumentDTO triés par score (descendant)
            Peut être vide si aucun document ne dépasse score_threshold

        Example:
            >>> command = SearchDocumentsCommand(
            ...     query="Développeur Python FastAPI",
            ...     limit=10,
            ...     score_threshold=0.5
            ... )
            >>> documents = use_case.execute(command)
            >>> print(len(documents))  # 0 à 10 documents
            >>> print(documents[0].score)  # >= 0.5
        """
        logger.info(
            "search_documents_use_case_started",
            query=command.query,
            limit=command.limit,
            threshold=command.score_threshold,
        )

        # Étape 1: Appeler le repository
        # Le repository convertit query → embedding → recherche Qdrant
        results = self.document_repository.search(
            query=command.query,
            limit=command.limit,
            score_threshold=command.score_threshold,
        )

        # Étape 2: Convertir dicts → DTOs
        # Les résultats de Qdrant sont des dicts, on les structure en DTOs
        documents = [
            DocumentDTO(
                id=doc["id"],
                text=doc["text"],
                score=doc["score"],
                source=doc["source"],
            )
            for doc in results
        ]

        logger.info(
            "search_documents_use_case_completed",
            documents_found=len(documents),
        )

        return documents
