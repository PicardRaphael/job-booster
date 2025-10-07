import threading
from app.domain.services.observability_service import IObservabilityService
from app.services.langfuse_service import get_langfuse_service


class LangfuseAdapter(IObservabilityService):
    """
    Adapter entre le domaine et le service concret Langfuse.
    Implémente IObservabilityService.
    """

    def __init__(self):
        self._service = get_langfuse_service()

    def create_trace(self, name: str, input_data: dict = None, output_data: dict = None):
        """Crée une trace Langfuse et la retourne."""
        trace = self._service.create_trace(name=name, input_data=input_data or {}, output_data=output_data or {})
        return trace

    def create_span(self, trace, name: str, input_data: dict = None, output_data: dict = None):
        """Crée un span rattaché à une trace existante."""
        return self._service.create_span(trace, name=name, input_data=input_data or {}, output_data=output_data or {})

    def flush(self, async_flush: bool = True):
        """Flush les traces Langfuse (asynchrone par défaut)."""
        if async_flush:
            threading.Thread(target=self._service.flush, daemon=True).start()
        else:
            self._service.flush()
