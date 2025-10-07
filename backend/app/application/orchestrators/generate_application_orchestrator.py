"""
Generate Application Orchestrator.

Application Layer - Clean Architecture

Orchestrateur qui compose tous les use cases pour générer une candidature complète.
Responsabilité: Coordonner le workflow, pas faire la logique métier.
"""

from app.application.commands import (
    AnalyzeJobOfferCommand,
    GenerateApplicationCommand,
    GenerateContentCommand,
    RerankDocumentsCommand,
    SearchDocumentsCommand,
)
from app.application.dtos import GenerationResultDTO
from app.application.use_cases import (
    AnalyzeJobOfferUseCase,
    GenerateCoverLetterUseCase,
    GenerateEmailUseCase,
    GenerateLinkedInUseCase,
    RerankDocumentsUseCase,
    SearchDocumentsUseCase,
)
from app.core.logging import get_logger
from app.domain.exceptions import NoDatabaseDocumentsError
from app.domain.services.observability_service import IObservabilityService
from app.infrastructure.observability.langfuse_service import LangfuseService

logger = get_logger(__name__)


class GenerateApplicationOrchestrator:
    """
    Orchestrateur: Génération complète de candidature.

    Responsabilité (SRP):
    - Coordonner les use cases (workflow)
    - Une seule raison de changer: si le workflow change

    Flow orchestré:
    1. Analyser l'offre d'emploi
    2. Chercher documents RAG
    3. Reranker documents
    4. Générer contenu
    5. Envoyer traces observabilité
    """

    def __init__(
        self,
        analyze_use_case: AnalyzeJobOfferUseCase,
        search_use_case: SearchDocumentsUseCase,
        rerank_use_case: RerankDocumentsUseCase,
        email_use_case: GenerateEmailUseCase,
        linkedin_use_case: GenerateLinkedInUseCase,
        letter_use_case: GenerateCoverLetterUseCase,
        observability_service: IObservabilityService,
    ):
        self.analyze_use_case = analyze_use_case
        self.search_use_case = search_use_case
        self.rerank_use_case = rerank_use_case
        self.observability_service = observability_service

        self.writer_use_cases = {
            "email": email_use_case,
            "linkedin": linkedin_use_case,
            "letter": letter_use_case,
        }

    async def execute(self, command: GenerateApplicationCommand) -> GenerationResultDTO:
        logger.info(
            "orchestrator_started",
            content_type=command.content_type,
            offer_length=len(command.job_offer.text),
        )

        # === ÉTAPE 1: Créer trace principale Langfuse ===
        trace = self.observability_service.log_trace(
            name=f"{command.content_type}_generation",
            input_data={
                "content_type": command.content_type,
                "job_offer": command.job_offer.text[:2000],  # limite de log
            },
        )
        # Propager la trace pour tous les spans décorés
        self.observability_service.adapter.current_trace = trace
        logger.info("orchestrator_trace_created", trace_id=getattr(trace, "id", "unknown"))

        # === ÉTAPE 2: Analyse de l'offre ===
        analyze_command = AnalyzeJobOfferCommand(
            job_offer=command.job_offer,
            trace_context=None,  # plus utilisé
            content_type=command.content_type,
        )
        analysis_dto = self.analyze_use_case.execute(analyze_command)
        logger.info(
            "orchestrator_analysis_completed",
            position=getattr(analysis_dto, "position", None),
            skills_count=len(getattr(analysis_dto, "key_skills", [])),
        )

        # === ÉTAPE 3: Recherche contextuelle (RAG) ===
        search_query = self._build_search_query_from_analysis(analysis_dto, command.content_type)
        search_command = SearchDocumentsCommand(
            query=search_query,
            limit=25,
            score_threshold=0.3,
        )
        documents_dto = await self.search_use_case.execute(search_command)
        logger.info("orchestrator_search_completed", documents_found=len(documents_dto))

        if not documents_dto:
            logger.error("orchestrator_no_documents_found")
            raise NoDatabaseDocumentsError(
                "Aucune donnée utilisateur trouvée. Veuillez ingérer vos documents."
            )

        # === ÉTAPE 4: Reranker les documents ===
        rerank_command = RerankDocumentsCommand(
            query=search_query,
            documents=documents_dto,
            top_k=10,
        )
        reranked_documents_dto = await self.rerank_use_case.execute(rerank_command)
        logger.info(
            "orchestrator_rerank_completed",
            documents_reranked=len(reranked_documents_dto),
        )

        # === ÉTAPE 5: Génération du contenu final ===
        writer_use_case = self.writer_use_cases.get(command.content_type)
        if not writer_use_case:
            raise ValueError(
                f"Content type invalide: {command.content_type}. "
                f"Valeurs acceptées: email, linkedin, letter"
            )

        generate_command = GenerateContentCommand(
            job_offer=command.job_offer,
            analysis=analysis_dto,
            documents=reranked_documents_dto,
            content_type=command.content_type,
        )
        generated_content = writer_use_case.execute(generate_command)
        logger.info(
            "orchestrator_generation_completed",
            content_length=len(generated_content),
        )

        # === ÉTAPE 6: Flush observabilité ===
        trace.output = {"content": generated_content}
        trace.flush()
        self.observability_service.flush()

        # === ÉTAPE 7: Retourner le résultat complet ===
        result = GenerationResultDTO(
            content=generated_content,
            content_type=command.content_type,
            sources=reranked_documents_dto,
            trace_id=getattr(trace, "id", "unknown"),
        )

        logger.info(
            "orchestrator_completed",
            content_type=command.content_type,
            trace_id=getattr(trace, "id", "unknown"),
        )

        return result

    def _build_search_query_from_analysis(self, analysis_dto, content_type: str) -> str:
        poste = next((
            v for v in [
                getattr(analysis_dto, "poste", None),
                getattr(analysis_dto, "position", None),
                getattr(analysis_dto, "job_title", None),
                getattr(analysis_dto, "title", None),
            ] if v
        ), "")

        entreprise = next((
            v for v in [
                getattr(analysis_dto, "entreprise", None),
                getattr(analysis_dto, "company", None),
            ] if v
        ), "")

        base_query_parts = [
            (poste or "candidature"),
            entreprise,
            "règles rédaction candidature",
            "RULESET:GLOBAL",
        ]
        base_query = " ".join(p for p in base_query_parts if p).strip()

        suffix_by_type = {
            "letter": " RULESET:LETTER",
            "email": " RULESET:EMAIL",
            "linkedin": " RULESET:LINKEDIN",
        }
        return base_query + suffix_by_type.get(content_type, "")
