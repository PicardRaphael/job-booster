"""
Job Analysis DTO.

Application Layer - Clean Architecture

DTO pour transférer les résultats d'analyse entre les use cases.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class JobAnalysisDTO:
    """
    Data Transfer Object pour l'analyse d'une offre.

    Responsabilité:
    - Transporter les données d'analyse entre use cases
    - Éviter de passer l'entity Domain partout
    - Faciliter la sérialisation (ex: retour API)

    Attributs:
        summary: Résumé complet de l'offre
        key_skills: Liste des compétences clés requises
        position: Intitulé du poste
        company: Nom de l'entreprise (peut être None)
    """

    summary: str
    key_skills: List[str]
    position: str
    company: str | None = None
