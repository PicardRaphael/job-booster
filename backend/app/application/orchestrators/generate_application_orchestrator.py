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
    TraceGenerationUseCase,
)
from app.core.logging import get_logger
from app.domain.exceptions import NoDatabaseDocumentsError
from app.domain.services.observability_service import IObservabilityService

logger = get_logger(__name__)


class GenerateApplicationOrchestrator:
    """
    Orchestrateur: Génération complète de candidature.

    Responsabilité (SRP):
    - Coordonner les use cases (workflow)
    - Une seule raison de changer: si le workflow change

    Flow orchestré:
    1. Créer trace d'observabilité (TraceGenerationUseCase)
    2. Analyser l'offre d'emploi (AnalyzeJobOfferUseCase)
    3. Chercher documents RAG (SearchDocumentsUseCase)
    4. Reranker documents (RerankDocumentsUseCase)
    5. Générer contenu (GenerateEmail/LinkedIn/Letter UseCase)
    6. Retourner résultat complet

    Pourquoi un orchestrateur?
    - Compose use cases atomiques (réutilisables)
    - Gère le workflow global
    - Une erreur dans une étape peut stopper le workflow
    - Facile de tester (mock les use cases)

    Note:
    L'orchestrateur ne fait PAS de logique métier.
    Il délègue tout aux use cases.
    """

    def __init__(
        self,
        trace_use_case: TraceGenerationUseCase,
        analyze_use_case: AnalyzeJobOfferUseCase,
        search_use_case: SearchDocumentsUseCase,
        rerank_use_case: RerankDocumentsUseCase,
        email_use_case: GenerateEmailUseCase,
        linkedin_use_case: GenerateLinkedInUseCase,
        letter_use_case: GenerateCoverLetterUseCase,
        observability_service: IObservabilityService,
    ):
        """
        Injecte tous les use cases nécessaires.

        Args:
            trace_use_case: Use case pour créer trace
            analyze_use_case: Use case pour analyser offre
            search_use_case: Use case pour chercher documents
            rerank_use_case: Use case pour reranker documents
            email_use_case: Use case pour générer email
            linkedin_use_case: Use case pour générer LinkedIn
            letter_use_case: Use case pour générer lettre
            observability_service: Service pour flush traces
        """
        self.trace_use_case = trace_use_case
        self.analyze_use_case = analyze_use_case
        self.search_use_case = search_use_case
        self.rerank_use_case = rerank_use_case
        self.observability_service = observability_service

        # Map content_type → use case
        # Permet de sélectionner le bon writer dynamiquement
        self.writer_use_cases = {
            "email": email_use_case,
            "linkedin": linkedin_use_case,
            "letter": letter_use_case,
        }

    async def execute(self, command: GenerateApplicationCommand) -> GenerationResultDTO:
        """
        Exécute le workflow complet de génération.

        Args:
            command: Command contenant job_offer et content_type

        Returns:
            GenerationResultDTO avec content, sources, trace_id

        Raises:
            InvalidJobOfferError: Si l'offre est invalide
            NoDatabaseDocumentsError: Si aucun document trouvé
            AnalysisFailedError: Si l'analyse échoue
            ContentGenerationError: Si la génération échoue

        Example:
            >>> command = GenerateApplicationCommand(
            ...     job_offer=JobOfferDTO(text="Développeur Python..."),
            ...     content_type="email"
            ... )
            >>> result = orchestrator.execute(command)
            >>> print(result.content)  # Email généré
            >>> print(len(result.sources))  # 3-5 sources
            >>> print(result.trace_id)  # "langfuse-abc123"
        """
        logger.info(
            "orchestrator_started",
            content_type=command.content_type,
            offer_length=len(command.job_offer.text),
        )

        # === ÉTAPE 1: Créer trace d'observabilité ===
        trace_dto = self.trace_use_case.execute(
            name="job_application_generation",
            metadata={
                "content_type": command.content_type,
                "offer_length": len(command.job_offer.text),
            },
        )
        logger.info("orchestrator_trace_created", trace_id=trace_dto.trace_id)

        # === ÉTAPE 2: Analyser l'offre d'emploi ===
        analyze_command = AnalyzeJobOfferCommand(
            job_offer=command.job_offer,
            trace_context=trace_dto,
            content_type=command.content_type,  # Pass content_type to analyzer
        )
        analysis_dto = self.analyze_use_case.execute(analyze_command)
        logger.info(
            "orchestrator_analysis_completed",
            position=analysis_dto.position,
            skills_count=len(analysis_dto.key_skills),
        )

        # === ÉTAPE 3: Chercher documents RAG ===
        search_query = self._build_search_query_from_analysis(analysis_dto, command.content_type)
        search_command = SearchDocumentsCommand(
            query=search_query,
            limit=10,  # Top 10 de Qdrant
            score_threshold=0.5,  # Minimum 50% similarité
        )
        documents_dto = await self.search_use_case.execute(search_command)
        logger.info(
            "orchestrator_search_completed",
            documents_found=len(documents_dto),
        )

        # Validation métier: documents requis
        if not documents_dto:
            logger.error("orchestrator_no_documents_found")
            raise NoDatabaseDocumentsError(
                "Aucune donnée utilisateur trouvée. Veuillez ingérer vos documents."
            )

        # === ÉTAPE 4: Reranker documents ===
        rerank_command = RerankDocumentsCommand(
            query=search_query,
            documents=documents_dto,
            top_k=5,  # Top 5 après reranking
        )
        reranked_documents_dto = await self.rerank_use_case.execute(rerank_command)
        logger.info(
            "orchestrator_rerank_completed",
            documents_reranked=len(reranked_documents_dto),
        )

        # === ÉTAPE 5: Générer contenu ===
        # Sélectionner le bon use case selon content_type
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

        # === ÉTAPE 6: Flush observability ===
        # S'assure que les traces sont envoyées à Langfuse
        self.observability_service.flush()

        # === ÉTAPE 7: Retourner résultat ===
        result = GenerationResultDTO(
            content=generated_content,
            content_type=command.content_type,
            sources=reranked_documents_dto,
            trace_id=trace_dto.trace_id,
        )

        logger.info(
            "orchestrator_completed",
            content_type=command.content_type,
            trace_id=trace_dto.trace_id,
        )

        return result

    def _build_search_query_from_analysis(self, analysis_dto, content_type: str) -> str:
        """
        Construit une query de recherche ULTRA-OPTIMISÉE depuis l'analyse.

        Combine TOUTES les infos de l'analyzer pour maximiser la pertinence:
        - Position + compétences techniques + soft skills
        - Secteur + valeurs + missions
        - Keywords spécifiques au content_type

        Args:
            analysis_dto: JobAnalysisDTO complet avec toutes les infos
            content_type: Type de contenu (letter, email, linkedin)

        Returns:
            Query string pour Qdrant ultra-optimisée
            Ex: "Développeur Python React FastAPI IA LangChain e-commerce innovation
                 autonomie React Next.js TypeScript lettre motivation RULESET LETTER"

        Stratégie:
            1. Position (poids le plus fort)
            2. Compétences techniques (top 5)
            3. Soft skills (si pertinentes)
            4. Secteur d'activité
            5. Valeurs entreprise
            6. Keywords content_type (RULESET)

        Cela permet au RAG de récupérer:
        - Les bons RULESETS
        - Les expériences pertinentes
        - Les compétences qui matchent
        """
        parts = []

        # 1. Position (toujours en premier)
        parts.append(analysis_dto.position)

        # 2. Compétences techniques (top 8 pour couvrir large)
        if analysis_dto.key_skills:
            parts.extend(analysis_dto.key_skills[:8])

        # 3. Secteur d'activité (aide à trouver expériences pertinentes)
        if analysis_dto.sector:
            parts.append(analysis_dto.sector)

        # 4. Valeurs entreprise (aide à personnaliser)
        if analysis_dto.values:
            # Top 3 valeurs maximum
            parts.extend(analysis_dto.values[:3])

        # 5. Soft skills pertinentes (top 3)
        if analysis_dto.soft_skills:
            parts.extend(analysis_dto.soft_skills[:3])

        # 6. Keywords content_type (CRUCIAL pour récupérer les bons RULESETS)
        content_keywords = {
            "letter": "lettre motivation RULESET LETTER Structure signature",
            "email": "email candidature message RULESET EMAIL court",
            "linkedin": "LinkedIn post message réseau RULESET LINKEDIN",
        }
        parts.append(content_keywords.get(content_type, ""))

        # 7. Ajout de keywords génériques pour maximiser retrieval
        parts.append("React Next.js TypeScript IA Python")  # Tes skills principaux

        query = " ".join(filter(None, parts))  # Remove empty strings
        logger.info("rag_search_query_built", query=query[:200])  # Log first 200 chars
        return query
