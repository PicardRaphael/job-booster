"""
Generate Application Command.

Application Layer - Clean Architecture

Command pour l'orchestrateur complet de génération.
"""

from dataclasses import dataclass

from app.application.dtos import JobOfferDTO


@dataclass
class GenerateApplicationCommand:
    """
    Command: Générer une candidature complète (orchestrateur).

    Intention:
    - Exécuter tout le flow de génération
    - Depuis l'offre brute jusqu'au contenu final
    - Flow: Analyze → Search → Rerank → Generate

    Attributs:
        job_offer: Offre d'emploi brute (texte)
        content_type: Type de contenu à générer
                     Valeurs: "email", "linkedin", "letter"

    Usage:
        >>> command = GenerateApplicationCommand(
        ...     job_offer=JobOfferDTO(text="Développeur Python..."),
        ...     content_type="email"
        ... )
        >>> result = orchestrator.execute(command)
        >>> print(result.content)  # Email généré
        >>> print(result.sources)  # Sources utilisées
        >>> print(result.trace_id)  # ID trace Langfuse

    Ce command est utilisé par l'API endpoint /generate.
    L'orchestrateur décompose ce command en plusieurs commands atomiques:
    1. AnalyzeJobOfferCommand
    2. SearchDocumentsCommand
    3. RerankDocumentsCommand
    4. GenerateContentCommand
    """

    job_offer: JobOfferDTO
    content_type: str  # "email", "linkedin", "letter"
