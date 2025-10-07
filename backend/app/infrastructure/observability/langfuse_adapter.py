"""Langfuse adapter implementing observability service interface."""

from app.domain.services.observability_service import IObservabilityService
from app.services.langfuse_service import get_langfuse_service


class LangfuseAdapter(IObservabilityService):
    """
    Adapter entre le domaine et Langfuse.
    Implémente IObservabilityService.

    Rôle:
    - Wrapper autour de LangfuseService
    - Maintenir la trace courante pour les spans
    - Implémenter l'interface domaine
    """

    def __init__(self):
        """Initialize avec le service Langfuse."""
        self._service = get_langfuse_service()
        self.current_trace = None  # Pour les spans décorés

    def create_trace(self, name: str, input_data: dict, output_data: dict = None):
        """
        Crée une trace Langfuse.

        Args:
            name: Nom de la trace
            input_data: Données d'entrée
            output_data: Données de sortie (optionnel)

        Returns:
            Objet trace Langfuse
        """
        trace = self._service.create_trace(name, input_data, output_data)
        self.current_trace = trace  # Garde pour les spans
        return trace

    def create_span(self, trace=None, name: str = None, input_data: dict = None, output_data: dict = None):
        """
        Crée un span dans une trace.

        Args:
            trace: Trace parent (ou None pour utiliser current_trace)
            name: Nom du span
            input_data: Données d'entrée
            output_data: Données de sortie

        Returns:
            Objet span Langfuse
        """
        trace_ref = trace or self.current_trace
        if not trace_ref:
            raise RuntimeError("Aucune trace courante définie pour le span Langfuse.")
        return self._service.create_span(trace_ref, name, input_data, output_data)

    def flush(self) -> None:
        """Flush les traces Langfuse."""
        self._service.flush()


def get_langfuse_adapter() -> LangfuseAdapter:
    """
    Récupère une instance de LangfuseAdapter.

    Returns:
        Instance de LangfuseAdapter
    """
    return LangfuseAdapter()
