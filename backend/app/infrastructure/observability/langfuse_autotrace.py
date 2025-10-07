import os
from app.infrastructure.observability.langfuse_decorator import trace_span

def autotrace_methods(cls):
    """
    Décorateur de classe : applique automatiquement @trace_span
    sur toutes les méthodes publiques de la classe.

    - Active uniquement si ENABLE_AGENT_TRACE=true dans l'environnement.
    - Ignore les méthodes privées (commençant par '_').
    """
    enable_trace = os.getenv("ENABLE_AGENT_TRACE", "false").lower() == "true"
    if not enable_trace:
        return cls  # Ne rien faire si désactivé

    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("_"):
            setattr(cls, attr_name, trace_span(f"{cls.__name__}.{attr_name}")(attr_value))
    return cls
