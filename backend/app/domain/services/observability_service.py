"""
Observability Service Interface.

Domain Layer - Clean Architecture
Interface (Port) pour le service d'observabilité (tracing, monitoring).

Pourquoi une interface?
- Permet de changer d'outil (Langfuse, Datadog, Honeycomb) sans changer le métier
- Facilite les tests (NoOpAdapter pour désactiver en tests)
- Respecte le Dependency Inversion Principle (DIP)

Exemple d'implémentations possibles:
- LangfuseAdapter (actuel)
- DatadogAdapter (pour APM Datadog)
- NoOpAdapter (pour tests ou désactiver observability)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class TraceContext:
    """
    Value Object représentant un contexte de trace.

    Immutable (frozen=True) car c'est une donnée qui ne change pas.

    Attributs:
        trace_id: Identifiant unique de la trace
                  Ex: "langfuse-abc123", "datadog-xyz789"
        metadata: Métadonnées associées à la trace
                  Ex: {"user_id": "123", "content_type": "email"}
    """

    trace_id: str
    metadata: Dict[str, Any]


class IObservabilityService(ABC):
    """
    Interface pour le service d'observabilité.

    Responsabilité:
    - Créer des traces pour suivre l'exécution
    - Associer des métadonnées aux opérations
    - Permettre le debug et le monitoring en production

    Note: Cette interface est simple intentionnellement.
    Si besoin de plus de features (spans, events, metrics),
    on peut étendre avec d'autres méthodes.
    """

    @abstractmethod
    def create_trace(self, name: str, metadata: Dict[str, Any]) -> TraceContext:
        """
        Crée une nouvelle trace d'observabilité.

        Utilisé pour:
        - Tracer une génération de contenu complète
        - Associer un ID unique à chaque requête
        - Stocker des métadonnées (type de contenu, longueur, etc.)

        Args:
            name: Nom de la trace (ex: "job_application_generation")
            metadata: Métadonnées associées
                     Ex: {"content_type": "email", "user_id": "123"}

        Returns:
            TraceContext avec trace_id et metadata

        Example:
            >>> service.create_trace(
            ...     name="generation",
            ...     metadata={"type": "email", "length": 500}
            ... )
            TraceContext(trace_id="langfuse-abc123", metadata={...})
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Force l'envoi des traces au serveur.

        Utilisé pour:
        - S'assurer que les traces sont envoyées avant la fin de la requête
        - Éviter de perdre des traces en cas de crash

        Note: Certains services (comme Langfuse) bufferisent les traces
        et les envoient par batch. Cette méthode force l'envoi immédiat.

        Example:
            >>> service.create_trace("test", {})
            >>> service.flush()  # Envoie au serveur maintenant
        """
        pass
