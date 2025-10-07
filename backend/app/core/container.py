"""
Dependency Injection Container.

Core Layer - Clean Architecture

Container qui wire toutes les dépendances selon le Dependency Inversion Principle.
Gère tous les services, use cases et orchestrateurs de l'application.
"""

import os
from typing import Optional

from app.core.llm_factory import LLMFactory
from app.core.logging import get_logger

# Domain interfaces
from app.domain.repositories.document_repository import IDocumentRepository
from app.domain.repositories.embedding_service import IEmbeddingService
from app.domain.repositories.llm_provider import ILLMProvider
from app.domain.services.analyzer_service import IAnalyzerService
from app.domain.services.observability_service import IObservabilityService
from app.domain.services.reranker_service import IRerankerService
from app.domain.services.writer_service import IContentWriterService

# Infrastructure
from app.infrastructure.ai import LLMProviderAdapter, RerankerAdapter
from app.infrastructure.ai.crewai import (
    CrewAIContentWriterService,
    EmailWriterAdapter,
    LetterWriterAdapter,
    LinkedInWriterAdapter,
)
from app.infrastructure.ai.crewai_analyzer_adapter import CrewAIAnalyzerAdapter
from app.infrastructure.config import YAMLConfigurationLoader
from app.infrastructure.vector_db import MultilingualEmbeddingAdapter, QdrantAdapter
from app.infrastructure.observability import LangfuseAdapter, NoOpObservabilityAdapter

# Legacy services
from app.services.qdrant_service import get_qdrant_service
from app.services.reranker import get_reranker_service

# Application use cases
from app.application.orchestrators import GenerateApplicationOrchestrator
from app.application.use_cases import (
    AnalyzeJobOfferUseCase,
    GenerateCoverLetterUseCase,
    GenerateEmailUseCase,
    GenerateLinkedInUseCase,
    RerankDocumentsUseCase,
    SearchDocumentsUseCase,
)

logger = get_logger(__name__)


class Container:
    """
    Dependency Injection Container (Singleton).

    Responsabilité:
    - Wire toutes les dépendances de l'application
    - Lazy initialization (création à la demande)
    - Singleton pattern (une seule instance)

    Architecture:
    Domain (interfaces) ← Application (use cases) ← Infrastructure (adapters) ← API
    """

    _instance: Optional["Container"] = None

    def __new__(cls) -> "Container":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # type: ignore
        return cls._instance

    def __init__(self) -> None:
        """Initialize container (lazy)."""
        if self._initialized:  # type: ignore
            return

        logger.info("initializing_dependency_container")

        # Config
        self._config_loader: Optional[YAMLConfigurationLoader] = None

        # Infrastructure
        self._llm_provider: Optional[ILLMProvider] = None
        self._embedding_service: Optional[IEmbeddingService] = None
        self._document_repository: Optional[IDocumentRepository] = None
        self._observability_service: Optional[IObservabilityService] = None

        # Domain services
        self._analyzer_service: Optional[IAnalyzerService] = None
        self._reranker_service: Optional[IRerankerService] = None
        self._content_writer_service: Optional[IContentWriterService] = None

        # Use cases
        self._analyze_use_case: Optional[AnalyzeJobOfferUseCase] = None
        self._search_use_case: Optional[SearchDocumentsUseCase] = None
        self._rerank_use_case: Optional[RerankDocumentsUseCase] = None
        self._email_use_case: Optional[GenerateEmailUseCase] = None
        self._linkedin_use_case: Optional[GenerateLinkedInUseCase] = None
        self._letter_use_case: Optional[GenerateCoverLetterUseCase] = None

        # Orchestrators
        self._orchestrator: Optional[GenerateApplicationOrchestrator] = None

        self._initialized = True  # type: ignore
        logger.info("dependency_container_initialized")

    # === Configuration ===

    def config_loader(self) -> YAMLConfigurationLoader:
        """Get config loader."""
        if self._config_loader is None:
            self._config_loader = YAMLConfigurationLoader()
        return self._config_loader

    # === Infrastructure ===

    def llm_provider(self) -> ILLMProvider:
        """Get LLM provider."""
        if self._llm_provider is None:
            config_loader = self.config_loader()
            llm_config = config_loader.load_llm_config()
            llm_factory = LLMFactory(llm_config)
            self._llm_provider = LLMProviderAdapter(llm_factory)
        return self._llm_provider

    def embedding_service(self) -> IEmbeddingService:
        """Get embedding service."""
        if self._embedding_service is None:
            self._embedding_service = MultilingualEmbeddingAdapter()
        return self._embedding_service

    def document_repository(self) -> IDocumentRepository:
        """Get document repository."""
        if self._document_repository is None:
            qdrant_service = get_qdrant_service()
            self._document_repository = QdrantAdapter(qdrant_service)
        return self._document_repository

    def observability_service(self) -> IObservabilityService:
        """Get observability service."""
        if self._observability_service is None:
            if os.getenv("ENABLE_LANGFUSE", "false").lower() == "true":
                self._observability_service = LangfuseAdapter()
            else:
                self._observability_service = NoOpObservabilityAdapter()
        return self._observability_service

    # === Domain Services ===

    def analyzer_service(self) -> IAnalyzerService:
        """Get analyzer service."""
        if self._analyzer_service is None:
            llm_provider = self.llm_provider()
            config_loader = self.config_loader()
            agent_config = config_loader.get_agent_config("analyzer")
            task_config = config_loader.get_task_config("analyze_offer")
            self._analyzer_service = CrewAIAnalyzerAdapter(
                llm_provider, agent_config, task_config
            )
        return self._analyzer_service

    def reranker_service(self) -> IRerankerService:
        """Get reranker service."""
        if self._reranker_service is None:
            self._reranker_service = RerankerAdapter()
        return self._reranker_service

    def content_writer_service(self) -> IContentWriterService:
        """Get content writer service (composite)."""
        if self._content_writer_service is None:
            llm_provider = self.llm_provider()
            config_loader = self.config_loader()

            # Email writer
            email_writer = EmailWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("email_writer"),
                config_loader.get_task_config("write_email"),
            )

            # LinkedIn writer
            linkedin_writer = LinkedInWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("linkedin_writer"),
                config_loader.get_task_config("write_linkedin"),
            )

            # Letter writer
            letter_writer = LetterWriterAdapter(
                llm_provider,
                config_loader.get_agent_config("letter_writer"),
                config_loader.get_task_config("write_letter"),
            )

            # Composite
            self._content_writer_service = CrewAIContentWriterService(
                email_writer, linkedin_writer, letter_writer
            )
        return self._content_writer_service

    # === Use Cases ===

    def analyze_use_case(self) -> AnalyzeJobOfferUseCase:
        """Get analyze use case."""
        if self._analyze_use_case is None:
            self._analyze_use_case = AnalyzeJobOfferUseCase(self.analyzer_service())
        return self._analyze_use_case

    def search_use_case(self) -> SearchDocumentsUseCase:
        """Get search use case."""
        if self._search_use_case is None:
            self._search_use_case = SearchDocumentsUseCase(self.document_repository())
        return self._search_use_case

    def rerank_use_case(self) -> RerankDocumentsUseCase:
        """Get rerank use case."""
        if self._rerank_use_case is None:
            self._rerank_use_case = RerankDocumentsUseCase(self.reranker_service())
        return self._rerank_use_case

    def email_use_case(self) -> GenerateEmailUseCase:
        """Get email use case."""
        if self._email_use_case is None:
            email_writer = self.content_writer_service().get_email_writer()
            self._email_use_case = GenerateEmailUseCase(email_writer)
        return self._email_use_case

    def linkedin_use_case(self) -> GenerateLinkedInUseCase:
        """Get LinkedIn use case."""
        if self._linkedin_use_case is None:
            linkedin_writer = self.content_writer_service().get_linkedin_writer()
            self._linkedin_use_case = GenerateLinkedInUseCase(linkedin_writer)
        return self._linkedin_use_case

    def letter_use_case(self) -> GenerateCoverLetterUseCase:
        """Get letter use case."""
        if self._letter_use_case is None:
            letter_writer = self.content_writer_service().get_letter_writer()
            self._letter_use_case = GenerateCoverLetterUseCase(letter_writer)
        return self._letter_use_case

    # === Orchestrators ===

    def generate_application_orchestrator(
        self,
    ) -> GenerateApplicationOrchestrator:
        """Get orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = GenerateApplicationOrchestrator(
                analyze_use_case=self.analyze_use_case(),
                search_use_case=self.search_use_case(),
                rerank_use_case=self.rerank_use_case(),
                email_use_case=self.email_use_case(),
                linkedin_use_case=self.linkedin_use_case(),
                letter_use_case=self.letter_use_case(),
                observability_service=self.observability_service(),
            )
        return self._orchestrator


_container: Optional[Container] = None


def get_container() -> Container:
    """Get container singleton."""
    global _container
    if _container is None:
        _container = Container()
    return _container
