"""
Multilingual Embedding Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour le service d'embeddings multilingue via HuggingFace API HTTP.
Impl�mente IEmbeddingService du domain.
"""

from typing import List

from app.core.logging import get_logger
from app.domain.repositories.embedding_service import IEmbeddingService
from app.services.huggingface_embeddings import get_hf_embedding_service

logger = get_logger(__name__)


class MultilingualEmbeddingAdapter(IEmbeddingService):
    """
    Adapter pour embeddings multilingues via HuggingFace API HTTP.

    Responsabilit� (SRP):
    - Wrapper le service d'embeddings HuggingFace HTTP API
    - Impl�menter l'interface IEmbeddingService
    - Une seule raison de changer: si le mod�le d'embedding change

    Pattern Adapter (Hexagonal Architecture):
    - Adapte le service embeddings HuggingFace � l'interface domain
    - Permet de changer de mod�le facilement via API HTTP
    - Isole le domain des d�tails d'impl�mentation

    Mod�les support�s:
    - intfloat/multilingual-e5-base (768 dim)
    - intfloat/multilingual-e5-large (1024 dim)
    - BAAI/bge-large-en-v1.5 (1024 dim)
    - Supporte: Fran�ais, Anglais, et 100+ langues

    Example:
        >>> adapter = MultilingualEmbeddingAdapter()
        >>> vectors = await adapter.embed_texts(["Python developer", "FastAPI expert"])
        >>> print(len(vectors))
        2
        >>> print(len(vectors[0]))
        768  # Dimension du mod�le (e5-base)
    """

    def __init__(self):
        """
        Initialise l'adapter avec le service d'embeddings HuggingFace.

        Note:
        On utilise get_hf_embedding_service() qui est un singleton.
        Utilise l'API HTTP de HuggingFace Inference.
        """
        self.embedding_service = get_hf_embedding_service()
        logger.info("multilingual_embedding_adapter_initialized")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convertit une liste de textes en vecteurs.

        Utilis� pour:
        - Ing�rer documents dans Qdrant (batch)
        - Vectoriser plusieurs phrases en une fois

        Args:
            texts: Liste de textes � vectoriser
                   Ex: ["Je suis dev Python", "J'aime FastAPI"]

        Returns:
            Liste de vecteurs (listes de floats)
            Ex: [[0.1, 0.5, ...], [0.3, 0.2, ...]]
            Chaque vecteur a dimension 1024

        Example:
            >>> texts = [
            ...     "D�veloppeur Python avec 5 ans d'exp�rience",
            ...     "Expert FastAPI et microservices"
            ... ]
            >>> vectors = await adapter.embed_texts(texts)
            >>> print(len(vectors))
            2
            >>> print(len(vectors[0]))
            1024
        """
        logger.info("embedding_texts", count=len(texts))

        # Appeler le service HuggingFace HTTP API
        vectors = await self.embedding_service.embed_texts(texts)

        logger.info(
            "texts_embedded",
            count=len(texts),
            dimension=len(vectors[0]) if vectors else 0,
        )

        return vectors

    async def embed_query(self, query: str) -> List[float]:
        """
        Convertit une requ�te en vecteur.

        Utilis� pour:
        - Chercher dans Qdrant avec une query
        - Optimis� pour les requ�tes (vs documents)

        Note:
        Certains mod�les ont des embeddings diff�rents pour
        queries vs documents (asymmetric search). Le mod�le
        multilingual-e5-large supporte cela.

        Args:
            query: Texte de la requ�te
                   Ex: "D�veloppeur Python FastAPI"

        Returns:
            Un vecteur (liste de floats)
            Ex: [0.2, 0.4, 0.1, ...]
            Dimension: 1024

        Example:
            >>> query = "D�veloppeur Python avec FastAPI"
            >>> vector = await adapter.embed_query(query)
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

        # Appeler le service HuggingFace HTTP API
        vector = await self.embedding_service.embed_text(query)

        logger.info("query_embedded", dimension=len(vector))

        return vector

    def get_dimension(self) -> int:
        """
        Retourne la dimension des vecteurs.

        Utilis� pour:
        - Cr�er la collection Qdrant avec la bonne dimension
        - Valider que les vecteurs ont la bonne taille

        Returns:
            Dimension des vecteurs (int)
            Pour multilingual-e5-large: 1024

        Example:
            >>> adapter = MultilingualEmbeddingAdapter()
            >>> dim = adapter.get_dimension()
            >>> print(dim)
            1024
            >>> # Utiliser pour cr�er collection Qdrant
            >>> qdrant_client.create_collection(
            ...     collection_name="docs",
            ...     vectors_config=VectorParams(
            ...         size=dim,  # � Dimension du mod�le
            ...         distance=Distance.COSINE
            ...     )
            ... )
        """
        dimension = self.embedding_service.get_dimension()

        logger.info("embedding_dimension_retrieved", dimension=dimension)

        return dimension
