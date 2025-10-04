"""
Trace Context DTO.

Application Layer - Clean Architecture

DTO pour transférer le contexte de trace entre use cases.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TraceContextDTO:
    """
    Data Transfer Object pour le contexte de trace.

    Responsabilité:
    - Transporter l'ID de trace entre use cases
    - Permettre de lier toutes les opérations à une même trace
    - Faciliter l'observabilité distribuée

    Attributs:
        trace_id: Identifiant unique de la trace
                  (ex: "langfuse-abc123")
        metadata: Métadonnées associées à la trace
                  (ex: {"user_id": "123", "content_type": "email"})

    Usage:
        # TraceUseCase crée la trace
        trace_dto = TraceContextDTO(
            trace_id="langfuse-abc123",
            metadata={"type": "email"}
        )

        # Autres use cases peuvent utiliser trace_id
        analyze_command = AnalyzeCommand(
            job_offer=...,
            trace_context=trace_dto  # Lien avec la trace
        )
    """

    trace_id: str
    metadata: Dict[str, Any]
