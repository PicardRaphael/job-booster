"""
Generate LinkedIn Message Use Case.

Application Layer - Clean Architecture

Use case atomique pour générer un message privé LinkedIn.
Responsabilité unique: Génération de message LinkedIn uniquement.
"""

from typing import List

from app.application.commands import GenerateContentCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.services.writer_service import ILinkedInWriter
from app.infrastructure.observability.langfuse_decorator import trace_span

logger = get_logger(__name__)


class GenerateLinkedInUseCase:
    """
    Use Case: Générer un message privé LinkedIn de motivation.

    Responsabilité (SRP):
    - Générer uniquement des messages privés LinkedIn
    - Une seule raison de changer: si le format message LinkedIn change

    Flow:
    1. Construire le contexte RAG depuis documents
    2. Convertir DTOs → Entities
    3. Appeler le writer service
    4. Retourner le contenu généré

    Pourquoi ce use case séparé?
    - Interface Segregation: Dépend de ILinkedInWriter uniquement
    - Réutilisable: On peut générer un message LinkedIn indépendamment
    - Testable: Mock ILinkedInWriter facilement
    """

    def __init__(self, linkedin_writer: ILinkedInWriter):
        """
        Injecte le writer de messages LinkedIn.

        Args:
            linkedin_writer: Writer pour générer messages privés LinkedIn (interface)
                            Ex: LinkedInWriterAdapter (avec CrewAI)
        """
        self.linkedin_writer = linkedin_writer

    @trace_span("GenerateLinkedInUseCase")
    def execute(self, command: GenerateContentCommand) -> str:
        """
        Génère un message privé LinkedIn de motivation.

        Args:
            command: Command contenant job_offer, analysis, documents

        Returns:
            Message privé LinkedIn (str)
            Format: Message direct, court (100-150 mots), sans emojis

        Raises:
            ContentGenerationError: Si la génération échoue

        Example:
            >>> command = GenerateContentCommand(
            ...     job_offer=JobOfferDTO(...),
            ...     analysis=JobAnalysisDTO(...),
            ...     documents=[doc1, doc2, doc3],
            ...     content_type="linkedin"
            ... )
            >>> message = use_case.execute(command)
            >>> print(message)
            "Bonjour [Prénom],\\n\\nJe me permets de vous contacter..."
        """
        logger.info("generate_linkedin_use_case_started")

        # Étape 1: Construire contexte RAG
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
        linkedin_content = self.linkedin_writer.write_linkedin_message(
            job_offer=job_offer,
            analysis=analysis,
            context=context,
        )

        logger.info(
            "generate_linkedin_use_case_completed",
            content_length=len(linkedin_content),
        )

        return linkedin_content

    def _build_rag_context(self, documents: List[DocumentDTO]) -> str:
        """
        Construit le contexte RAG depuis les documents.

        Args:
            documents: Liste de documents (expériences utilisateur)

        Returns:
            Contexte formaté (str)

        Note:
            Même logique que generate_email.py
            On pourrait extraire dans un helper partagé si besoin.
        """
        if not documents:
            logger.warning("generate_linkedin_no_rag_context")
            return ""

        context_parts = [
            f"Source: {doc.source}\n{doc.text}"
            for doc in documents
        ]

        return "\n\n".join(context_parts)
