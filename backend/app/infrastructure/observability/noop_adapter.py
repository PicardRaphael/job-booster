"""No-op observability adapter for testing or when observability is disabled."""

from app.domain.services.observability_service import IObservabilityService


class NoOpObservabilityAdapter(IObservabilityService):
    """
    No-operation adapter for observability.

    Used when observability is disabled or for testing.
    All methods are no-ops and return dummy objects.
    """

    def create_trace(self, name: str, input_data: dict, output_data: dict = None):
        """Create a no-op trace that returns None."""
        return None

    def create_span(self, trace, name: str = None, input_data: dict = None, output_data: dict = None):
        """Create a no-op span that returns None."""
        return None

    def flush(self) -> None:
        """No-op flush."""
        pass
