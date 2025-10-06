"""Langfuse observability service."""

from typing import Any, Dict

from langfuse import Langfuse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LangfuseService:
    """Service for Langfuse tracing and observability."""

    def __init__(self) -> None:
        """Initialize Langfuse client."""
        logger.info("initializing_langfuse")
        self.client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        logger.info("langfuse_initialized")

    def create_trace(
        self,
        name: str,
        user_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Any:
        """Create a new trace."""
        trace_id = self.client.create_trace_id()
        # Return a simple object with the trace_id
        return type('Trace', (), {'id': trace_id, 'name': name, 'metadata': metadata or {}})()

    def flush(self) -> None:
        """Flush all pending events to Langfuse."""
        self.client.flush()


# Singleton instance
_langfuse_service: LangfuseService | None = None


def get_langfuse_service() -> LangfuseService:
    """Get or create the singleton Langfuse service."""
    global _langfuse_service
    if _langfuse_service is None:
        _langfuse_service = LangfuseService()
    return _langfuse_service
