"""
Search Documents Command.

Application Layer - Clean Architecture

Command pour chercher des documents dans la base vectorielle.
"""

from dataclasses import dataclass


@dataclass
class SearchDocumentsCommand:
    """
    Command: Chercher des documents dans Qdrant.

    Intention:
    - Rechercher des documents similaires à une query
    - Utiliser la recherche sémantique (embeddings)
    - Filtrer par score de similarité

    Attributs:
        query: Texte de recherche (sera converti en embedding)
               Ex: "Développeur Python FastAPI Docker"
        limit: Nombre max de documents à retourner (default: 10)
        score_threshold: Score minimum de similarité (0.0 à 1.0)
                        Default: 0.5 (50% de similarité minimum)

    Usage:
        >>> command = SearchDocumentsCommand(
        ...     query="Développeur Python FastAPI",
        ...     limit=10,
        ...     score_threshold=0.5
        ... )
        >>> documents = search_use_case.execute(command)
        >>> print(len(documents))  # Max 10 documents
    """

    query: str
    limit: int = 10
    score_threshold: float = 0.5
