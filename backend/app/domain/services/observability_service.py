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


class IObservabilityService(ABC):
    """
    Interface pour le service d'observabilité compatible avec Langfuse.

    Responsabilité:
    - Créer des traces pour suivre l'exécution
    - Créer des spans pour tracer les sous-étapes
    - Permettre le debug et le monitoring en production

    Design:
    - Signature compatible avec Langfuse (input_data, output_data)
    - Retourne l'objet trace/span natif pour permettre l'extension
    - Méthodes optionnelles pour flexibilité
    """

    @abstractmethod
    def create_trace(self, name: str, input_data: dict, output_data: dict = None):
        """
        Crée une nouvelle trace d'observabilité.

        Args:
            name: Nom de la trace (ex: "job_application_generation")
            input_data: Données d'entrée de l'opération
                       Ex: {"job_offer": "...", "content_type": "email"}
            output_data: Données de sortie (optionnel)
                        Ex: {"generated_text": "...", "length": 500}

        Returns:
            Objet trace natif (ex: Langfuse trace object)

        Example:
            >>> trace = service.create_trace(
            ...     name="generation",
            ...     input_data={"type": "email"},
            ...     output_data={"length": 500}
            ... )
        """
        pass

    @abstractmethod
    def create_span(self, trace, name: str = None, input_data: dict = None, output_data: dict = None):
        """
        Crée un span (sous-étape) dans une trace.

        Args:
            trace: Objet trace parent
            name: Nom du span (ex: "rag_search")
            input_data: Données d'entrée du span
            output_data: Données de sortie du span

        Returns:
            Objet span natif

        Example:
            >>> span = service.create_span(
            ...     trace=trace,
            ...     name="rag_search",
            ...     input_data={"query": "..."},
            ...     output_data={"results": 10}
            ... )
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Force l'envoi des traces au serveur.

        Example:
            >>> service.flush()  # Envoie toutes les traces buffered
        """
        pass
