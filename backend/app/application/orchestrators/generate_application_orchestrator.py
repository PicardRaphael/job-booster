"""
Generate Application Orchestrator.

Application Layer - Clean Architecture

Orchestrateur qui compose tous les use cases pour générer une candidature complète.
Responsabilité : Coordonner le workflow, pas faire la logique métier.
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

logger = get_logger(__name__)


class GenerateApplicationOrchestrator:
    """
    Orchestrateur : Génération complète de candidature.

    Flow :
    1. Crée la trace principale (Langfuse)
    2. Analyse l’offre d’emploi
    3. Recherche contextuelle (RAG)
    4. Rerank des documents
    5. Génération du contenu final
    6. Flush asynchrone de l’observabilité
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

        # === ÉTAPE 1: Créer la trace principale ===
        try:
            trace = self.observability_service.create_trace(
                name=f"generate_{command.content_type}_workflow",
                input_data={
                    "content_type": command.content_type,
                    "offer_excerpt": command.job_offer.text[:300],
                },
            )
            main_span = self.observability_service.create_span(trace, "full_workflow")
            logger.info("orchestrator_trace_created", trace_id=getattr(trace, "id", "noop"))
        except Exception as e:
            logger.warning("orchestrator_trace_failed", error=str(e))
            trace = None
            main_span = None

        try:
            # === ÉTAPE 2: Analyse de l’offre ===
            analyze_command = AnalyzeJobOfferCommand(
                job_offer=command.job_offer,
                trace_context=trace,
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
            search_command = SearchDocumentsCommand(query=search_query, limit=25, score_threshold=0.3)
            documents_dto = await self.search_use_case.execute(search_command)
            logger.info("orchestrator_search_completed", documents_found=len(documents_dto))

            if not documents_dto:
                raise NoDatabaseDocumentsError("Aucun document utilisateur trouvé dans Qdrant.")

            # === ÉTAPE 4: Rerank des documents ===
            rerank_command = RerankDocumentsCommand(query=search_query, documents=documents_dto, top_k=10)
            reranked_documents_dto = await self.rerank_use_case.execute(rerank_command)
            logger.info("orchestrator_rerank_completed", documents_reranked=len(reranked_documents_dto))

            # === ÉTAPE 5: Génération du contenu final ===
            writer_use_case = self.writer_use_cases.get(command.content_type)
            if not writer_use_case:
                raise ValueError(f"Type de contenu invalide: {command.content_type}")

            generate_command = GenerateContentCommand(
                job_offer=command.job_offer,
                analysis=analysis_dto,
                documents=reranked_documents_dto,
                content_type=command.content_type,
            )
            generated_content = writer_use_case.execute(generate_command)
            logger.info("orchestrator_generation_completed", content_length=len(generated_content))

            # === Enregistre sortie dans la trace ===
            if main_span:
                main_span.output = {"content_length": len(generated_content)}

        except Exception as e:
            if main_span:
                main_span.output = {"error": str(e)}
            raise e

        finally:
            # === Flush non bloquant de Langfuse ===
            if self.observability_service:
                self.observability_service.flush(async_flush=True)

        # === ÉTAPE 6: Retourner le résultat complet ===
        return GenerationResultDTO(
            content=generated_content,
            content_type=command.content_type,
            sources=reranked_documents_dto,
            trace_id=getattr(trace, "id", "unknown"),
        )

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
