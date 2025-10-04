"""
Content Writer Service (Composite).

Infrastructure Layer - Clean Architecture

Service composite qui regroupe tous les writers.
Impl�mente IContentWriterService du domain.
"""

from app.core.logging import get_logger
from app.domain.services.writer_service import (
    IContentWriterService,
    IEmailWriter,
    ILetterWriter,
    ILinkedInWriter,
)

logger = get_logger(__name__)


class CrewAIContentWriterService(IContentWriterService):
    """
    Service composite pour tous les writers CrewAI.

    Responsabilit� (SRP):
    - Fournir acc�s aux 3 writers (email, LinkedIn, lettre)
    - Une seule raison de changer: si on ajoute/supprime un type de writer

    Pattern Composite:
    - Regroupe les 3 writers en un seul service
    - Facilite la Dependency Injection (1 service au lieu de 3)
    - Respecte Interface Segregation (chaque writer reste s�par�)

    Pourquoi ce service?
    - Le Container injecte 1 seul service au lieu de 3
    - Partage des ressources entre writers (config, LLM provider)
    - Centralise la logique de s�lection du bon writer

    Example:
        >>> service = CrewAIContentWriterService(
        ...     email_writer=EmailWriterAdapter(...),
        ...     linkedin_writer=LinkedInWriterAdapter(...),
        ...     letter_writer=LetterWriterAdapter(...)
        ... )
        >>> # Utilisation
        >>> email_writer = service.get_email_writer()
        >>> email = email_writer.write_email(job_offer, analysis, context)
    """

    def __init__(
        self,
        email_writer: IEmailWriter,
        linkedin_writer: ILinkedInWriter,
        letter_writer: ILetterWriter,
    ):
        """
        Initialise le service composite avec les 3 writers.

        Args:
            email_writer: Writer pour emails (IEmailWriter)
            linkedin_writer: Writer pour LinkedIn (ILinkedInWriter)
            letter_writer: Writer pour lettres (ILetterWriter)

        Note:
        Les writers sont inject�s (d�j� cr��s par le Container).
        Ce service est juste un wrapper/composite.
        """
        self._email_writer = email_writer
        self._linkedin_writer = linkedin_writer
        self._letter_writer = letter_writer
        logger.info("crewai_content_writer_service_initialized")

    def get_email_writer(self) -> IEmailWriter:
        """
        Retourne le writer pour emails.

        Returns:
            Instance de IEmailWriter (EmailWriterAdapter)

        Example:
            >>> writer = service.get_email_writer()
            >>> email = writer.write_email(job_offer, analysis, context)
        """
        return self._email_writer

    def get_linkedin_writer(self) -> ILinkedInWriter:
        """
        Retourne le writer pour LinkedIn.

        Returns:
            Instance de ILinkedInWriter (LinkedInWriterAdapter)

        Example:
            >>> writer = service.get_linkedin_writer()
            >>> message = writer.write_linkedin_message(job_offer, analysis, context)
        """
        return self._linkedin_writer

    def get_letter_writer(self) -> ILetterWriter:
        """
        Retourne le writer pour lettres.

        Returns:
            Instance de ILetterWriter (LetterWriterAdapter)

        Example:
            >>> writer = service.get_letter_writer()
            >>> letter = writer.write_cover_letter(job_offer, analysis, context)
        """
        return self._letter_writer
