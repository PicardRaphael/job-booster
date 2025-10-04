"""
Rerank Documents Command.

Application Layer - Clean Architecture

Command pour reranker des documents par pertinence.
"""

from dataclasses import dataclass
from typing import List

from app.application.dtos import DocumentDTO


@dataclass
class RerankDocumentsCommand:
    """
    Command: Reranker des documents par pertinence.

    Intention:
    - Affiner l'ordre des documents trouvés par Qdrant
    - Utiliser un modèle de reranking plus précis
    - Garder seulement les top_k documents les plus pertinents

    Pourquoi reranker?
    - Qdrant fait une recherche rapide mais approximative
    - Le reranker est plus lent mais plus précis
    - Flow optimal: Qdrant (top 10) → Reranker (top 5)

    Attributs:
        query: Query originale de recherche
        documents: Documents à reranker (de Qdrant)
        top_k: Nombre de documents à garder (default: 5)

    Usage:
        >>> documents = search_use_case.execute(...)  # 10 docs de Qdrant
        >>> command = RerankDocumentsCommand(
        ...     query="Python FastAPI",
        ...     documents=documents,
        ...     top_k=5
        ... )
        >>> reranked = rerank_use_case.execute(command)
        >>> print(len(reranked))  # 5 docs (les meilleurs)
    """

    query: str
    documents: List[DocumentDTO]
    top_k: int = 5
