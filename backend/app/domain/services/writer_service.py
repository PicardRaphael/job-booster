"""
Writer Services Interfaces.

Domain Layer - Clean Architecture
Interfaces (Ports) pour les services de génération de contenu.

Pourquoi 3 interfaces séparées au lieu d'une seule?
- Interface Segregation Principle (ISP): "Les clients ne doivent pas dépendre
  d'interfaces qu'ils n'utilisent pas"
- Chaque type de contenu (email, LinkedIn, lettre) a ses spécificités
- Permet d'avoir des implémentations spécialisées par type
- Plus facile à tester et à mocker

Architecture:
- IEmailWriter: Génère des emails de motivation
- ILinkedInWriter: Génère des posts LinkedIn
- ILetterWriter: Génère des lettres de motivation
- IContentWriterService: Composite qui donne accès aux 3 writers
"""

from abc import ABC, abstractmethod

from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer


class IEmailWriter(ABC):
    """
    Interface pour générer des emails de motivation.

    Responsabilité:
    - Générer un email court et impactant
    - Utiliser le contexte RAG pour personnaliser
    - S'adapter au ton et style email professionnel
    """

    @abstractmethod
    def write_email(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """
        Génère un email de motivation.

        Args:
            job_offer: Offre d'emploi originale (texte brut)
            analysis: Analyse structurée de l'offre
                     (position, skills, company)
            context: Contexte RAG (expériences/projets de l'utilisateur)

        Returns:
            Email de motivation (str)
            Format attendu: Objet + Corps du message

        Example:
            >>> writer.write_email(job_offer, analysis, context)
            "Objet: Candidature Développeur Python\\n\\nBonjour,\\n..."
        """
        pass


class ILinkedInWriter(ABC):
    """
    Interface pour générer des posts LinkedIn.

    Responsabilité:
    - Générer un post engageant pour LinkedIn
    - Utiliser le contexte RAG pour montrer l'expérience
    - S'adapter au ton LinkedIn (professionnel mais humain)
    """

    @abstractmethod
    def write_linkedin_post(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """
        Génère un post LinkedIn de motivation.

        Args:
            job_offer: Offre d'emploi originale (texte brut)
            analysis: Analyse structurée de l'offre
                     (position, skills, company)
            context: Contexte RAG (expériences/projets de l'utilisateur)

        Returns:
            Post LinkedIn (str)
            Format: Post direct avec hashtags

        Example:
            >>> writer.write_linkedin_post(job_offer, analysis, context)
            "🚀 Développeur Python passionné recherche nouveau défi!\\n..."
        """
        pass


class ILetterWriter(ABC):
    """
    Interface pour générer des lettres de motivation.

    Responsabilité:
    - Générer une lettre formelle et structurée
    - Utiliser le contexte RAG pour détailler l'expérience
    - S'adapter au ton formel (lettre classique)
    """

    @abstractmethod
    def write_cover_letter(
        self,
        job_offer: JobOffer,
        analysis: JobAnalysis,
        context: str,
    ) -> str:
        """
        Génère une lettre de motivation.

        Args:
            job_offer: Offre d'emploi originale (texte brut)
            analysis: Analyse structurée de l'offre
                     (position, skills, company)
            context: Contexte RAG (expériences/projets de l'utilisateur)

        Returns:
            Lettre de motivation (str)
            Format: Lettre formelle avec en-tête, corps, signature

        Example:
            >>> writer.write_cover_letter(job_offer, analysis, context)
            "Madame, Monsieur,\\n\\nJe vous adresse ma candidature..."
        """
        pass


class IContentWriterService(ABC):
    """
    Interface composite pour accéder à tous les writers.

    Pourquoi un composite?
    - Facilite la Dependency Injection (1 seul service au lieu de 3)
    - Permet de partager des ressources entre writers (ex: même LLM)
    - Centralise la configuration des writers

    Usage:
        >>> service = container.content_writer_service()
        >>> email_writer = service.get_email_writer()
        >>> linkedin_writer = service.get_linkedin_writer()
    """

    @abstractmethod
    def get_email_writer(self) -> IEmailWriter:
        """
        Retourne le writer pour emails.

        Returns:
            Instance de IEmailWriter
        """
        pass

    @abstractmethod
    def get_linkedin_writer(self) -> ILinkedInWriter:
        """
        Retourne le writer pour LinkedIn.

        Returns:
            Instance de ILinkedInWriter
        """
        pass

    @abstractmethod
    def get_letter_writer(self) -> ILetterWriter:
        """
        Retourne le writer pour lettres.

        Returns:
            Instance de ILetterWriter
        """
        pass
