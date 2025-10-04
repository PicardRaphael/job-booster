"""
Langfuse Observability Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour intégrer Langfuse (service d'observabilité).
Implémente IObservabilityService du domain.
"""

from typing import Any, Dict

from app.core.logging import get_logger
from app.domain.services.observability_service import (
    IObservabilityService,
    TraceContext,
)
from app.services.langfuse_service import get_langfuse_service

logger = get_logger(__name__)


class LangfuseAdapter(IObservabilityService):
    """
    Adapter Langfuse pour observabilité.

    Responsabilité (SRP):
    - Wrapper le service Langfuse legacy
    - Implémenter l'interface IObservabilityService
    - Une seule raison de changer: si l'API Langfuse change

    Pattern Adapter:
    - Adapte le service Langfuse existant à l'interface domain
    - Permet de changer de service d'observabilité facilement
    - Isole le domain des détails d'implémentation Langfuse

    Example:
        >>> adapter = LangfuseAdapter()
        >>> trace = adapter.create_trace(
        ...     name="generation",
        ...     metadata={"type": "email"}
        ... )
        >>> print(trace.trace_id)
        "langfuse-abc123..."
    """

    def __init__(self):
        """
        Initialise l'adapter avec le service Langfuse.

        Note:
        On utilise get_langfuse_service() qui est un singleton.
        Cela évite de créer plusieurs connexions Langfuse.
        """
        self.langfuse = get_langfuse_service()
        logger.info("langfuse_adapter_initialized")

    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        """
        Crée une trace Langfuse.

        Args:
            name: Nom de la trace (ex: "job_application_generation")
            metadata: Métadonnées à associer
                     Ex: {"content_type": "email", "user_id": "123"}

        Returns:
            TraceContext avec trace_id et metadata

        Example:
            >>> trace = adapter.create_trace(
            ...     name="generation",
            ...     metadata={"type": "email", "length": 500}
            ... )
            >>> print(trace.trace_id)
            "langfuse-abc123-xyz789"
        """
        logger.info("creating_langfuse_trace", name=name)

        # Appeler le service Langfuse legacy
        langfuse_trace = self.langfuse.create_trace(name=name, metadata=metadata)

        # Extraire trace_id
        # Langfuse peut retourner différents formats, on gère les cas
        if hasattr(langfuse_trace, "id"):
            trace_id = str(langfuse_trace.id)
        elif isinstance(langfuse_trace, dict) and "id" in langfuse_trace:
            trace_id = str(langfuse_trace["id"])
        else:
            # Fallback si format inconnu
            trace_id = "unknown"
            logger.warning(
                "langfuse_trace_id_extraction_failed",
                trace_type=type(langfuse_trace).__name__,
            )

        # Convertir en TraceContext (domain entity)
        trace_context = TraceContext(trace_id=trace_id, metadata=metadata)

        logger.info("langfuse_trace_created", trace_id=trace_id)

        return trace_context

    def flush(self) -> None:
        """
        Force l'envoi des traces à Langfuse.

        Langfuse buffer les traces et les envoie par batch.
        Cette méthode force l'envoi immédiat.

        Important:
        À appeler avant la fin d'une requête pour s'assurer
        que toutes les traces sont envoyées.

        Example:
            >>> adapter.create_trace("test", {})
            >>> adapter.flush()  # Envoie maintenant
        """
        logger.info("flushing_langfuse_traces")
        self.langfuse.flush()
        logger.info("langfuse_traces_flushed")
