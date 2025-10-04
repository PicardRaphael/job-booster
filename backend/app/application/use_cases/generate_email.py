"""
Generate Email Use Case.

Application Layer - Clean Architecture

Use case atomique pour générer un email de motivation.
Responsabilité unique: Génération d'email uniquement.
"""

from typing import List

from app.application.commands import GenerateContentCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.services.writer_service import IEmailWriter

logger = get_logger(__name__)


class GenerateEmailUseCase:
    """
    Use Case: Générer un email de motivation.

    Responsabilité (SRP):
    - Générer uniquement des emails
    - Une seule raison de changer: si le format email change

    Flow:
    1. Construire le contexte RAG depuis documents
    2. Convertir DTOs → Entities
    3. Appeler le writer service
    4. Retourner le contenu généré

    Pourquoi ce use case séparé?
    - Interface Segregation: Dépend de IEmailWriter uniquement
    - Réutilisable: On peut générer un email indépendamment
    - Testable: Mock IEmailWriter facilement
    """

    def __init__(self, email_writer: IEmailWriter):
        """
        Injecte le writer d'emails.

        Args:
            email_writer: Writer pour générer emails (interface)
                         Ex: EmailWriterAdapter (avec CrewAI)
        """
        self.email_writer = email_writer

    def execute(self, command: GenerateContentCommand) -> str:
        """
        Génère un email de motivation.

        Args:
            command: Command contenant job_offer, analysis, documents

        Returns:
            Email de motivation (str)
            Format: "Objet: ...\n\nBonjour,\n..."

        Raises:
            ContentGenerationError: Si la génération échoue

        Example:
            >>> command = GenerateContentCommand(
            ...     job_offer=JobOfferDTO(...),
            ...     analysis=JobAnalysisDTO(...),
            ...     documents=[doc1, doc2, doc3],
            ...     content_type="email"
            ... )
            >>> email = use_case.execute(command)
            >>> print(email)
            "Objet: Candidature Développeur Python\\n\\nBonjour,..."
        """
        logger.info("generate_email_use_case_started")

        # Étape 1: Construire contexte RAG
        # Les documents sont convertis en texte pour le prompt
        context = self._build_rag_context(command.documents)

        # Étape 2: Convertir DTOs → Entities (validation)
        job_offer = JobOffer(text=command.job_offer.text)
        analysis = JobAnalysis(
            summary=command.analysis.summary,
            key_skills=command.analysis.key_skills,
            position=command.analysis.position,
            company=command.analysis.company,
        )

        # Étape 3: Appeler le writer
        # Le writer utilise un agent AI pour générer l'email
        email_content = self.email_writer.write_email(
            job_offer=job_offer,
            analysis=analysis,
            context=context,
        )

        logger.info(
            "generate_email_use_case_completed",
            content_length=len(email_content),
        )

        return email_content

    def _build_rag_context(self, documents: List[DocumentDTO]) -> str:
        """
        Construit le contexte RAG depuis les documents.

        Le contexte est un string formaté qui sera injecté dans le prompt
        de l'agent AI pour personnaliser l'email.

        Args:
            documents: Liste de documents (expériences utilisateur)

        Returns:
            Contexte formaté (str)
            Ex: "Source: cv.pdf\nExpérience Python...\n\nSource: projet.md\n..."

        Note:
            Si aucun document, retourne string vide.
            L'agent AI générera quand même un email (moins personnalisé).
        """
        if not documents:
            logger.warning("generate_email_no_rag_context")
            return ""

        # Formater chaque document avec sa source
        context_parts = [
            f"Source: {doc.source}\n{doc.text}"
            for doc in documents
        ]

        # Joindre avec double saut de ligne pour séparer les sources
        return "\n\n".join(context_parts)
