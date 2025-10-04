"""
Document DTO.

Application Layer - Clean Architecture

DTO pour transférer les documents RAG entre les use cases.
"""

from dataclasses import dataclass


@dataclass
class DocumentDTO:
    """
    Data Transfer Object pour un document RAG.

    Responsabilité:
    - Transporter un document Qdrant entre use cases
    - Stocker score original ET score après reranking
    - Faciliter le passage entre SearchUseCase et RerankUseCase

    Attributs:
        id: Identifiant unique du document dans Qdrant
        text: Contenu textuel du document
        score: Score de similarité original (Qdrant cosine)
        source: Source du document (ex: "cv.pdf", "projet_x.md")
        rerank_score: Score après reranking (None si pas encore reranked)
    """

    id: str
    text: str
    score: float  # Score Qdrant (0.0 à 1.0)
    source: str
    rerank_score: float | None = None  # Score après reranking (optionnel)
