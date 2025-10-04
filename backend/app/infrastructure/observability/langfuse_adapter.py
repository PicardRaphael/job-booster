"""
Langfuse Observability Adapter.

Infrastructure Layer - Clean Architecture

Adapter pour int�grer Langfuse (service d'observabilit�).
Impl�mente IObservabilityService du domain.
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
    Adapter Langfuse pour observabilit�.

    Responsabilit� (SRP):
    - Wrapper le service Langfuse legacy
    - Impl�menter l'interface IObservabilityService
    - Une seule raison de changer: si l'API Langfuse change

    Pattern Adapter:
    - Adapte le service Langfuse existant � l'interface domain
    - Permet de changer de service d'observabilit� facilement
    - Isole le domain des d�tails d'impl�mentation Langfuse

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
        Cela �vite de cr�er plusieurs connexions Langfuse.
        """
        self.langfuse = get_langfuse_service()
        logger.info("langfuse_adapter_initialized")

    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        """
        Cr�e une trace Langfuse.

        Args:
            name: Nom de la trace (ex: "job_application_generation")
            metadata: M�tadonn�es � associer
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
        # Langfuse peut retourner diff�rents formats, on g�re les cas
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
        Force l'envoi des traces � Langfuse.

        Langfuse buffer les traces et les envoie par batch.
        Cette m�thode force l'envoi imm�diat.

        Important:
        � appeler avant la fin d'une requ�te pour s'assurer
        que toutes les traces sont envoy�es.

        Example:
            >>> adapter.create_trace("test", {})
            >>> adapter.flush()  # Envoie maintenant
        """
        logger.info("flushing_langfuse_traces")
        self.langfuse.flush()
        logger.info("langfuse_traces_flushed")
