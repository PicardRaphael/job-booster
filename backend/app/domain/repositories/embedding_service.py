"""
Embedding Service Interface.

Domain Layer - Clean Architecture
Interface (Port) pour le service d'embeddings.

Pourquoi une interface?
- Permet de changer de modèle d'embedding sans changer le code métier
- Facilite les tests (on peut créer un FakeEmbeddingService)
- Respecte le Dependency Inversion Principle (DIP)

Exemple d'implémentations possibles:
- MultilingualEmbeddingAdapter (actuel avec HuggingFace API HTTP)
- OpenAIEmbeddingAdapter (avec text-embedding-3-small)
- LocalEmbeddingAdapter (avec sentence-transformers en local)
"""

from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    """
    Interface pour le service d'embeddings vectoriels.

    Responsabilité:
    - Convertir du texte en vecteurs numériques
    - Permettre la recherche sémantique dans Qdrant

    Note: Cette interface est dans 'repositories' car elle représente
    un accès à une resource externe (modèle d'embedding).
    """

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convertit une liste de textes en vecteurs (async).

        Utilisé pour:
        - Ingérer des documents dans Qdrant (batch)
        - Embedder plusieurs phrases en une fois

        Args:
            texts: Liste de textes à vectoriser
                   Ex: ["Je suis développeur Python", "J'aime FastAPI"]

        Returns:
            Liste de vecteurs (listes de floats)
            Ex: [[0.1, 0.5, ...], [0.3, 0.2, ...]]
            Chaque vecteur a la même dimension (get_dimension())

        Raises:
            EmbeddingError: Si l'embedding échoue

        Note:
            Méthode async car utilise l'API HTTP HuggingFace
        """
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """
        Convertit une seule requête en vecteur (async).

        Utilisé pour:
        - Chercher dans Qdrant avec une query
        - Optimisé pour les requêtes (vs documents)

        Note: Certains modèles ont des embeddings différents
        pour queries vs documents (asymmetric search).

        Args:
            query: Texte de la requête
                   Ex: "Développeur Python FastAPI"

        Returns:
            Un seul vecteur (liste de floats)
            Ex: [0.2, 0.4, 0.1, ...]

        Raises:
            EmbeddingError: Si l'embedding échoue

        Note:
            Méthode async car utilise l'API HTTP HuggingFace
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Retourne la dimension des vecteurs générés.

        Utilisé pour:
        - Créer la collection Qdrant avec la bonne dimension
        - Valider que tous les vecteurs ont la même taille

        Returns:
            Dimension des vecteurs (int)
            Ex: 1024 pour multilingual-e5-large
                1536 pour text-embedding-3-small (OpenAI)

        Note: Cette valeur dépend du modèle utilisé et ne change jamais.
        """
        pass
