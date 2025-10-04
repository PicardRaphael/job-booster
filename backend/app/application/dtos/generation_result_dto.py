"""
Generation Result DTO.

Application Layer - Clean Architecture

DTO pour retourner le résultat de génération complet.
"""

from dataclasses import dataclass
from typing import List

from app.application.dtos.document_dto import DocumentDTO


@dataclass
class GenerationResultDTO:
    """
    Data Transfer Object pour le résultat de génération.

    Responsabilité:
    - Retourner tous les résultats de l'orchestrateur
    - Inclure le contenu généré + sources + trace
    - Faciliter la conversion vers GenerateResponse (API)

    Attributs:
        content: Contenu généré (email, LinkedIn, ou lettre)
        content_type: Type de contenu ("email", "linkedin", "letter")
        sources: Liste des documents sources utilisés (après reranking)
        trace_id: ID de la trace Langfuse (pour debugging)

    Usage:
        # Orchestrateur retourne ce DTO
        result = GenerationResultDTO(
            content="Objet: Candidature...",
            content_type="email",
            sources=[doc1, doc2, doc3],
            trace_id="langfuse-abc123"
        )

        # API Mapper convertit DTO → Response
        response = mapper.result_to_response(result)
    """

    content: str
    content_type: str
    sources: List[DocumentDTO]
    trace_id: str | None = None
