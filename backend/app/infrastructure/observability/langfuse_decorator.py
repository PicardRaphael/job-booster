import functools
import inspect
from app.infrastructure.observability.langfuse_adapter import LangfuseAdapter

# Singleton de l’adapter pour toute l’application
observability = LangfuseAdapter()


def trace_span(name: str):
    """
    Décorateur pour tracer automatiquement une méthode ou fonction comme span Langfuse.

    - Si une trace est active (current_trace), le span y est rattaché.
    - Enregistre input/output automatiquement.
    - Compatible avec fonctions sync ou async.
    """

    def decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace = observability.current_trace
            if not trace:
                # Pas de trace active, exécution normale
                return await func(*args, **kwargs)

            # Préparer les inputs
            input_data = {
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }

            # Créer le span
            span = observability.create_span(
                trace=trace,
                name=name,
                input_data=input_data,
            )

            try:
                result = await func(*args, **kwargs)
                span.output = {"result": str(result)[:2000]}  # limite taille
                return result
            except Exception as e:
                span.output = {"error": str(e)}
                raise
            finally:
                span.flush()

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            trace = observability.current_trace
            if not trace:
                # Pas de trace active, exécution normale
                return func(*args, **kwargs)

            input_data = {
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }

            span = observability.create_span(
                trace=trace,
                name=name,
                input_data=input_data,
            )

            try:
                result = func(*args, **kwargs)
                span.output = {"result": str(result)[:2000]}
                return result
            except Exception as e:
                span.output = {"error": str(e)}
                raise
            finally:
                span.flush()

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator
