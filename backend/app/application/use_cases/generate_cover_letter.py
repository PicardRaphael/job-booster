"""
Generate Cover Letter Use Case.

Application Layer - Clean Architecture

Use case atomique pour générer une lettre de motivation.
Responsabilité unique: Génération de lettre uniquement.
"""

from typing import List

from app.application.commands import GenerateContentCommand
from app.application.dtos import DocumentDTO
from app.core.logging import get_logger
from app.domain.entities.job_analysis import JobAnalysis
from app.domain.entities.job_offer import JobOffer
from app.domain.services.writer_service import ILetterWriter

logger = get_logger(__name__)


class GenerateCoverLetterUseCase:
    """
    Use Case: Générer une lettre de motivation.

    Responsabilité (SRP):
    - Générer uniquement des lettres de motivation
    - Une seule raison de changer: si le format lettre change

    Flow:
    1. Construire le contexte RAG depuis documents
    2. Convertir DTOs → Entities
    3. Appeler le writer service
    4. Retourner le contenu généré

    Pourquoi ce use case séparé?
    - Interface Segregation: Dépend de ILetterWriter uniquement
    - Réutilisable: On peut générer une lettre indépendamment
    - Testable: Mock ILetterWriter facilement
    """

    def __init__(self, letter_writer: ILetterWriter):
        """
        Injecte le writer de lettres.

        Args:
            letter_writer: Writer pour générer lettres (interface)
                          Ex: LetterWriterAdapter (avec CrewAI)
        """
        self.letter_writer = letter_writer

    def execute(self, command: GenerateContentCommand) -> str:
        """
        Génère une lettre de motivation.

        Args:
            command: Command contenant job_offer, analysis, documents

        Returns:
            Lettre de motivation (str)
            Format: Lettre formelle avec en-tête, corps, signature

        Raises:
            ContentGenerationError: Si la génération échoue

        Example:
            >>> command = GenerateContentCommand(
            ...     job_offer=JobOfferDTO(...),
            ...     analysis=JobAnalysisDTO(...),
            ...     documents=[doc1, doc2, doc3],
            ...     content_type="letter"
            ... )
            >>> letter = use_case.execute(command)
            >>> print(letter)
            "Madame, Monsieur,\\n\\nJe vous adresse ma candidature..."
        """
        logger.info("generate_cover_letter_use_case_started")

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
        letter_content = self.letter_writer.write_cover_letter(
            job_offer=job_offer,
            analysis=analysis,
            context=context,
        )

        logger.info(
            "generate_cover_letter_use_case_completed",
            content_length=len(letter_content),
        )

        return letter_content

    def _build_rag_context(self, documents: List[DocumentDTO]) -> str:
        """
        Construit le contexte RAG depuis les documents.

        Args:
            documents: Liste de documents (expériences utilisateur)

        Returns:
            Contexte formaté (str)

        Note:
            Même logique que generate_email.py et generate_linkedin.py
            Si cela devient plus complexe, on pourrait créer un
            RAGContextBuilder service.
        """
        if not documents:
            logger.warning("generate_cover_letter_no_rag_context")
            return ""

        context_parts = [
            f"Source: {doc.source}\n{doc.text}"
            for doc in documents
        ]

        return "\n\n".join(context_parts)
