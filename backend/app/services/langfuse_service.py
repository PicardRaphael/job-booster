from langfuse import Langfuse
from app.core.config import settings

_langfuse_instance = None


class LangfuseService:
    """Service concret qui gère le client Langfuse."""

    def __init__(self):
        self.client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

    def create_trace(self, name: str, input_data: dict, output_data: dict = None):
        trace = self.client.trace(
            name=name,
            input=input_data,
            output=output_data,
        )
        trace.flush()
        return trace

    def create_span(self, trace, name: str, input_data: dict = None, output_data: dict = None):
        span = trace.span(
            name=name,
            input=input_data,
            output=output_data,
        )
        span.flush()
        return span

    def flush(self):
        try:
            self.client.flush()
        except Exception as e:
            print(f"[Langfuse flush error] {e}")


def get_langfuse_service() -> LangfuseService:
    """Singleton getter pour le service Langfuse."""
    global _langfuse_instance
    if _langfuse_instance is None:
        _langfuse_instance = LangfuseService()
    return _langfuse_instance
