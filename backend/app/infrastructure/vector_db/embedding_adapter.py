"""
Multilingual Embedding Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour le service d'embeddings multilingue.
ImplÈmente IEmbeddingService du domain.
"""

from typing import List

from app.core.logging import get_logger
from app.domain.repositories.embedding_service import IEmbeddingService
from app.services.embeddings import get_embedding_service

logger = get_logger(__name__)


class MultilingualEmbeddingAdapter(IEmbeddingService):
    """
    Adapter pour embeddings multilingues.

    ResponsabilitÈ (SRP):
    - Wrapper le service d'embeddings legacy
    - ImplÈmenter l'interface IEmbeddingService
    - Une seule raison de changer: si le modËle d'embedding change

    Pattern Adapter (Hexagonal Architecture):
    - Adapte le service embeddings existant ‡ l'interface domain
    - Permet de changer de modËle facilement (OpenAI, Cohere, etc.)
    - Isole le domain des dÈtails d'implÈmentation

    ModËle utilisÈ:
    - intfloat/multilingual-e5-large
    - Dimension: 1024
    - Supporte: FranÁais, Anglais, et 100+ langues

    Example:
        >>> adapter = MultilingualEmbeddingAdapter()
        >>> vectors = adapter.embed_texts(["Python developer", "FastAPI expert"])
        >>> print(len(vectors))
        2
        >>> print(len(vectors[0]))
        1024  # Dimension du modËle
    """

    def __init__(self):
        """
        Initialise l'adapter avec le service d'embeddings.

        Note:
        On utilise get_embedding_service() qui est un singleton.
        Le modËle est chargÈ une seule fois en mÈmoire.
        """
        self.embedding_service = get_embedding_service()
        logger.info("multilingual_embedding_adapter_initialized")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convertit une liste de textes en vecteurs.

        UtilisÈ pour:
        - IngÈrer documents dans Qdrant (batch)
        - Vectoriser plusieurs phrases en une fois

        Args:
            texts: Liste de textes ‡ vectoriser
                   Ex: ["Je suis dev Python", "J'aime FastAPI"]

        Returns:
            Liste de vecteurs (listes de floats)
            Ex: [[0.1, 0.5, ...], [0.3, 0.2, ...]]
            Chaque vecteur a dimension 1024

        Example:
            >>> texts = [
            ...     "DÈveloppeur Python avec 5 ans d'expÈrience",
            ...     "Expert FastAPI et microservices"
            ... ]
            >>> vectors = adapter.embed_texts(texts)
            >>> print(len(vectors))
            2
            >>> print(len(vectors[0]))
            1024
        """
        logger.info("embedding_texts", count=len(texts))

        # Appeler le service legacy
        vectors = self.embedding_service.embed_texts(texts)

        logger.info(
            "texts_embedded",
            count=len(texts),
            dimension=len(vectors[0]) if vectors else 0,
        )

        return vectors

    def embed_query(self, query: str) -> List[float]:
        """
        Convertit une requÍte en vecteur.

        UtilisÈ pour:
        - Chercher dans Qdrant avec une query
        - OptimisÈ pour les requÍtes (vs documents)

        Note:
        Certains modËles ont des embeddings diffÈrents pour
        queries vs documents (asymmetric search). Le modËle
        multilingual-e5-large supporte cela.

        Args:
            query: Texte de la requÍte
                   Ex: "DÈveloppeur Python FastAPI"

        Returns:
            Un vecteur (liste de floats)
            Ex: [0.2, 0.4, 0.1, ...]
            Dimension: 1024

        Example:
            >>> query = "DÈveloppeur Python avec FastAPI"
            >>> vector = adapter.embed_query(query)
            >>> print(len(vector))
            1024
            >>> # Utiliser pour recherche Qdrant
            >>> results = qdrant_client.search(
            ...     collection_name="docs",
            ...     query_vector=vector,
            ...     limit=10
            ... )
        """
        logger.info("embedding_query", query_preview=query[:50])

        # Appeler le service legacy
        vector = self.embedding_service.embed_query(query)

        logger.info("query_embedded", dimension=len(vector))

        return vector

    def get_dimension(self) -> int:
        """
        Retourne la dimension des vecteurs.

        UtilisÈ pour:
        - CrÈer la collection Qdrant avec la bonne dimension
        - Valider que les vecteurs ont la bonne taille

        Returns:
            Dimension des vecteurs (int)
            Pour multilingual-e5-large: 1024

        Example:
            >>> adapter = MultilingualEmbeddingAdapter()
            >>> dim = adapter.get_dimension()
            >>> print(dim)
            1024
            >>> # Utiliser pour crÈer collection Qdrant
            >>> qdrant_client.create_collection(
            ...     collection_name="docs",
            ...     vectors_config=VectorParams(
            ...         size=dim,  # ê Dimension du modËle
            ...         distance=Distance.COSINE
            ...     )
            ... )
        """
        dimension = self.embedding_service.get_dimension()

        logger.info("embedding_dimension_retrieved", dimension=dimension)

        return dimension
