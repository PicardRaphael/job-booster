"""
Job Offer DTO.

Application Layer - Clean Architecture

DTO pour transférer les données d'offre d'emploi entre les couches.
"""

from dataclasses import dataclass


@dataclass
class JobOfferDTO:
    """
    Data Transfer Object pour une offre d'emploi.

    Responsabilité:
    - Transporter le texte de l'offre entre API et Use Cases
    - Pas de validation (c'est le rôle de l'Entity dans Domain)
    - Pas de comportement métier (juste data)

    Utilisation:
        # API reçoit request
        dto = JobOfferDTO(text=request.job_offer)

        # Use Case convertit DTO → Entity
        job_offer = JobOffer(text=dto.text)  # ← Validation ici
    """

    text: str  # Texte brut de l'offre d'emploi
