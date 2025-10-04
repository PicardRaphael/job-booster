"""
Analyze Job Offer Command.

Application Layer - Clean Architecture

Command pour déclencher l'analyse d'une offre d'emploi.
"""

from dataclasses import dataclass

from app.application.dtos import JobOfferDTO, TraceContextDTO


@dataclass
class AnalyzeJobOfferCommand:
    """
    Command: Analyser une offre d'emploi.

    Intention:
    - Extraire les informations structurées d'une offre
    - Identifier: position, compétences, entreprise
    - Créer un résumé pour la recherche RAG

    Usage:
        >>> command = AnalyzeJobOfferCommand(
        ...     job_offer=JobOfferDTO(text="Développeur Python..."),
        ...     trace_context=TraceContextDTO(trace_id="123", metadata={})
        ... )
        >>> result = analyze_use_case.execute(command)
        >>> print(result.position)
        "Développeur Python"
    """

    job_offer: JobOfferDTO  # Offre à analyser
    trace_context: TraceContextDTO | None = None  # Contexte de trace (optionnel)
