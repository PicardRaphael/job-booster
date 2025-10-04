"""
No-Op Observability Adapter.

Infrastructure Layer - Clean Architecture

Adapter vide pour d�sactiver l'observabilit� (tests, dev).
Impl�mente IObservabilityService sans rien faire.
"""

from typing import Any, Dict

from app.core.logging import get_logger
from app.domain.services.observability_service import (
    IObservabilityService,
    TraceContext,
)

logger = get_logger(__name__)


class NoOpObservabilityAdapter(IObservabilityService):
    """
    Adapter No-Op pour observabilit�.

    Responsabilit� (SRP):
    - Impl�menter IObservabilityService sans action
    - Permettre de d�sactiver l'observabilit� facilement
    - Une seule raison de changer: si l'interface change

    Pourquoi un No-Op adapter?
    - Tests: Pas besoin de Langfuse pour tester
    - Dev: D�velopper sans compte Langfuse
    - Performance: D�sactiver observability en prod si besoin
    - Null Object Pattern: �vite les if/else partout

    Example d'usage:
        >>> # En tests
        >>> adapter = NoOpObservabilityAdapter()
        >>> trace = adapter.create_trace("test", {})
        >>> print(trace.trace_id)
        "noop"  # Pas de vraie trace cr��e

        >>> # Dans le Container (tests)
        >>> def observability_service():
        ...     if settings.environment == "test":
        ...         return NoOpObservabilityAdapter()
        ...     else:
        ...         return LangfuseAdapter()
    """

    def __init__(self):
        """
        Initialise l'adapter No-Op.

        Aucune connexion, aucune d�pendance externe.
        """
        logger.info("noop_observability_adapter_initialized")

    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        """
        "Cr�e" une trace factice.

        Ne fait rien, retourne juste un TraceContext avec ID "noop".

        Args:
            name: Nom de la trace (ignor�)
            metadata: M�tadonn�es (conserv�es pour coh�rence)

        Returns:
            TraceContext avec trace_id="noop"

        Example:
            >>> adapter = NoOpObservabilityAdapter()
            >>> trace = adapter.create_trace(
            ...     name="generation",
            ...     metadata={"type": "email"}
            ... )
            >>> print(trace.trace_id)
            "noop"
            >>> print(trace.metadata)
            {"type": "email"}
        """
        logger.debug(
            "noop_trace_created",
            name=name,
            metadata_keys=list(metadata.keys()),
        )

        # Retourner TraceContext factice
        return TraceContext(trace_id="noop", metadata=metadata)

    def flush(self) -> None:
        """
        "Flush" factice.

        Ne fait rien (pas de traces � envoyer).

        Example:
            >>> adapter = NoOpObservabilityAdapter()
            >>> adapter.flush()  # Ne fait rien
        """
        logger.debug("noop_flush_called")
        # Rien � faire
        pass
