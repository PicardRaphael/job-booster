"""
Generate Content Command.

Application Layer - Clean Architecture

Command pour générer du contenu (email, LinkedIn, lettre).
"""

from dataclasses import dataclass
from typing import List

from app.application.dtos import DocumentDTO, JobAnalysisDTO, JobOfferDTO


@dataclass
class GenerateContentCommand:
    """
    Command: Générer du contenu de candidature.

    Intention:
    - Générer un email, message privé LinkedIn, ou lettre de motivation
    - Utiliser l'analyse de l'offre + contexte RAG
    - Personnaliser avec les expériences de l'utilisateur

    Attributs:
        job_offer: Offre d'emploi originale
        analysis: Analyse structurée de l'offre
        documents: Documents RAG (expériences utilisateur)
        content_type: Type de contenu à générer
                     Valeurs: "email", "linkedin", "letter"

    Usage:
        >>> command = GenerateContentCommand(
        ...     job_offer=job_offer_dto,
        ...     analysis=analysis_dto,
        ...     documents=reranked_docs,
        ...     content_type="email"
        ... )
        >>> content = generate_email_use_case.execute(command)
        >>> print(content)  # "Objet: Candidature..."
    """

    job_offer: JobOfferDTO
    analysis: JobAnalysisDTO
    documents: List[DocumentDTO]
    content_type: str  # "email", "linkedin", "letter"
