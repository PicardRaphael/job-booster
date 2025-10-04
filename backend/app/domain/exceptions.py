"""
Domain Exceptions - Business Errors.

Domain Layer - Clean Architecture
Ces exceptions représentent des erreurs métier, pas des erreurs techniques.
Elles sont levées par les use cases et catchées par l'API.

Pourquoi dans Domain?
- Ce sont des règles métier (ex: "pas de documents = erreur")
- Indépendantes de l'infrastructure (pas liées à HTTP, DB, etc.)
- Réutilisables dans tous les use cases
"""


class DomainException(Exception):
    """
    Exception de base pour toutes les erreurs métier.

    Toutes les exceptions métier héritent de celle-ci.
    Permet de catcher toutes les erreurs business en une fois si besoin.
    """

    pass


class NoDatabaseDocumentsError(DomainException):
    """
    Erreur levée quand aucun document n'est trouvé dans la base de données.

    Cas d'usage:
    - L'utilisateur n'a pas encore ingéré ses documents CV/projets
    - La recherche RAG ne retourne aucun résultat
    - Le score de similarité est trop bas pour tous les documents

    Cette erreur est transformée en HTTP 404 par l'API.
    """

    def __init__(
        self, message: str = "Aucune donnée utilisateur trouvée. Veuillez ingérer vos documents."
    ):
        """
        Initialise l'erreur avec un message par défaut.

        Args:
            message: Message d'erreur personnalisé (optionnel)
        """
        super().__init__(message)
        self.message = message


class InvalidJobOfferError(DomainException):
    """
    Erreur levée quand l'offre d'emploi est invalide.

    Cas d'usage:
    - Texte trop court (< 50 caractères)
    - Texte vide
    - Format non reconnu

    Cette erreur est transformée en HTTP 400 par l'API.
    """

    def __init__(self, message: str = "L'offre d'emploi est invalide"):
        """
        Initialise l'erreur avec un message par défaut.

        Args:
            message: Message d'erreur personnalisé (optionnel)
        """
        super().__init__(message)
        self.message = message


class AnalysisFailedError(DomainException):
    """
    Erreur levée quand l'analyse de l'offre échoue.

    Cas d'usage:
    - Le LLM ne retourne pas de réponse valide
    - L'analyse ne peut pas extraire les informations nécessaires
    - Timeout du service d'analyse

    Cette erreur est transformée en HTTP 500 par l'API.
    """

    def __init__(self, message: str = "L'analyse de l'offre d'emploi a échoué"):
        """
        Initialise l'erreur avec un message par défaut.

        Args:
            message: Message d'erreur personnalisé (optionnel)
        """
        super().__init__(message)
        self.message = message


class ContentGenerationError(DomainException):
    """
    Erreur levée quand la génération de contenu échoue.

    Cas d'usage:
    - Le LLM ne retourne pas de contenu
    - Le contenu généré est vide
    - Timeout du service de génération

    Cette erreur est transformée en HTTP 500 par l'API.
    """

    def __init__(self, message: str = "La génération de contenu a échoué"):
        """
        Initialise l'erreur avec un message par défaut.

        Args:
            message: Message d'erreur personnalisé (optionnel)
        """
        super().__init__(message)
        self.message = message
