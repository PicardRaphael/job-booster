"""
Observability Adapters.

Infrastructure Layer - Clean Architecture

Adapters pour les services d'observabilité (tracing, monitoring).

Adapters disponibles:
- LangfuseAdapter: Intégration avec Langfuse
- NoOpAdapter: Adapter vide pour tests
"""

from app.infrastructure.observability.langfuse_adapter import LangfuseAdapter
from app.infrastructure.observability.noop_adapter import NoOpObservabilityAdapter

__all__ = ["LangfuseAdapter", "NoOpObservabilityAdapter"]
