"""
Trace Generation Use Case.

Application Layer - Clean Architecture

Use case atomique pour créer une trace d'observabilité.
Responsabilité unique: Gestion des traces (Langfuse, etc.).
"""

from typing import Any, Dict

from app.application.dtos import TraceContextDTO
from app.core.logging import get_logger
from app.domain.services.observability_service import IObservabilityService

logger = get_logger(__name__)


class TraceGenerationUseCase:
    """
    Use Case: Créer une trace d'observabilité.

    Responsabilité (SRP):
    - Créer des traces pour tracking
    - Une seule raison de changer: si la logique de tracing change

    Flow:
    1. Appeler le service d'observabilité
    2. Convertir TraceContext → DTO
    3. Retourner le DTO avec trace_id

    Pourquoi ce use case?
    - Sépare observability de la logique métier (SRP)
    - Peut créer une trace indépendamment
    - Facile de désactiver (NoOpAdapter) en tests
    - Respecte Single Responsibility

    Note sur l'architecture:
    Certains pourraient argumenter que le tracing devrait être dans
    un middleware/decorator. Mais avoir un use case permet:
    - De contrôler explicitement quand on trace
    - De lier la trace aux données métier (metadata)
    - De tester le tracing facilement
    """

    def __init__(self, observability_service: IObservabilityService):
        """
        Injecte le service d'observabilité.

        Args:
            observability_service: Service pour créer traces (interface)
                                  Ex: LangfuseAdapter, DatadogAdapter,
                                      NoOpAdapter (pour tests)
        """
        self.observability_service = observability_service

    def execute(self, name: str, metadata: Dict[str, Any]) -> TraceContextDTO:
        """
        Crée une trace d'observabilité.

        Args:
            name: Nom de la trace (ex: "job_application_generation")
            metadata: Métadonnées à associer à la trace
                     Ex: {"content_type": "email", "user_id": "123"}

        Returns:
            TraceContextDTO avec trace_id et metadata

        Example:
            >>> trace_dto = use_case.execute(
            ...     name="job_application_generation",
            ...     metadata={
            ...         "content_type": "email",
            ...         "offer_length": 500,
            ...         "user_id": "123"
            ...     }
            ... )
            >>> print(trace_dto.trace_id)
            "langfuse-abc123-xyz789"

            # Le trace_id peut ensuite être utilisé par d'autres use cases
            # pour lier leurs opérations à cette trace
        """
        logger.info("trace_generation_use_case_started", name=name)

        # Étape 1: Créer la trace via le service
        # Le service gère la communication avec Langfuse (ou autre)
        trace_context = self.observability_service.create_trace(
            name=name,
            metadata=metadata,
        )

        # Étape 2: Convertir Entity → DTO
        # On retourne un DTO pour découpler les couches
        trace_dto = TraceContextDTO(
            trace_id=trace_context.trace_id,
            metadata=trace_context.metadata,
        )

        logger.info(
            "trace_generation_use_case_completed",
            trace_id=trace_dto.trace_id,
        )

        return trace_dto
