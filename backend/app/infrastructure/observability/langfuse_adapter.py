from app.domain.interfaces.observability_service import IObservabilityService
from app.services.langfuse_service import get_langfuse_service


class LangfuseAdapter(IObservabilityService):
    """
    Adapter entre le domaine et le service concret Langfuse.
    Implémente IObservabilityService.

    Rôle :
    - Centraliser toutes les interactions avec Langfuse.
    - Maintenir la trace courante (`current_trace`) pour le décorateur @trace_span.
    """

    def __init__(self):
        self._service = get_langfuse_service()
        self.current_trace = None  # permet aux spans décorés de s'y rattacher

    # === TRACES ===

    def create_trace(self, name: str, input_data: dict, output_data: dict = None):
        """Crée une trace Langfuse et la stocke en trace courante."""
        trace = self._service.create_trace(name, input_data, output_data)
        self.current_trace = trace
        return trace

    def log_trace(self, name: str, input_data: dict, output_data: dict = None):
        """Alias de create_trace pour compatibilité avec orchestrateur."""
        return self.create_trace(name, input_data, output_data)

    # === SPANS ===

    def create_span(
        self, trace=None, name: str = None, input_data: dict = None, output_data: dict = None
    ):
        """
        Crée un span rattaché à la trace courante (si définie),
        sinon à la trace passée en argument.
        """
        trace_ref = trace or self.current_trace
        if not trace_ref:
            raise RuntimeError("Aucune trace courante définie pour le span Langfuse.")
        return self._service.create_span(trace_ref, name, input_data, output_data)

    # === FLUSH ===

    def flush(self):
        """Flush les traces Langfuse."""
        self._service.flush()
