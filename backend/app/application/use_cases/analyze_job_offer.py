"""
Analyze Job Offer Use Case.

Application Layer - Clean Architecture

Use case atomique pour analyser une offre d'emploi.
Responsabilité unique: Extraire informations structurées d'une offre.
"""

from app.application.commands import AnalyzeJobOfferCommand
from app.application.dtos import JobAnalysisDTO
from app.core.logging import get_logger
from app.domain.entities.job_offer import JobOffer
from app.domain.services.analyzer_service import IAnalyzerService

logger = get_logger(__name__)


class AnalyzeJobOfferUseCase:
    """
    Use Case: Analyser une offre d'emploi.

    Responsabilité (SRP):
    - Transformer offre brute → analyse structurée
    - Une seule raison de changer: si la logique d'analyse change

    Flow:
    1. Convertir DTO → Entity (validation)
    2. Appeler service domain (IAnalyzerService)
    3. Convertir Entity → DTO (pour retour)

    Pourquoi ce use case?
    - Réutilisable: On peut juste analyser sans générer
    - Testable: Mock IAnalyzerService facilement
    - Découplé: Si on change l'analyzer, ce code ne change pas
    """

    def __init__(self, analyzer_service: IAnalyzerService):
        """
        Injecte le service d'analyse.

        Args:
            analyzer_service: Service pour analyser l'offre (interface)
                             Ex: CrewAIAnalyzerAdapter, OpenAIAnalyzerAdapter
        """
        self.analyzer_service = analyzer_service

    def execute(self, command: AnalyzeJobOfferCommand) -> JobAnalysisDTO:
        """
        Exécute l'analyse de l'offre.

        Args:
            command: Command contenant l'offre à analyser

        Returns:
            JobAnalysisDTO avec summary, skills, position, company

        Raises:
            InvalidJobOfferError: Si l'offre est invalide (< 50 chars)
            AnalysisFailedError: Si l'analyse échoue

        Example:
            >>> command = AnalyzeJobOfferCommand(
            ...     job_offer=JobOfferDTO(text="Développeur Python...")
            ... )
            >>> result = use_case.execute(command)
            >>> print(result.position)
            "Développeur Python"
            >>> print(result.key_skills)
            ["Python", "FastAPI", "Docker"]
        """
        logger.info("analyze_job_offer_use_case_started")

        # Étape 1: Convertir DTO → Domain Entity
        # Cette conversion déclenche la validation (50 chars minimum)
        job_offer = JobOffer(text=command.job_offer.text)

        # Étape 2: Appeler le service domain
        # Le service utilise un agent AI pour extraire les informations
        analysis = self.analyzer_service.analyze(job_offer)

        # Étape 3: Convertir Entity → DTO
        # On retourne un DTO pour découpler les couches
        result = JobAnalysisDTO(
            summary=analysis.summary,
            key_skills=analysis.key_skills,
            position=analysis.position,
            company=analysis.company,
        )

        logger.info(
            "analyze_job_offer_use_case_completed",
            position=result.position,
            skills_count=len(result.key_skills),
        )

        return result
