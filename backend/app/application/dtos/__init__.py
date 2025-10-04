"""
Data Transfer Objects (DTOs).

Application Layer - Clean Architecture

Pourquoi des DTOs?
- Découpler les couches (Domain ↔ Application ↔ API)
- Si on change l'entité Domain, on ne casse pas l'API
- Permet de ne transférer que les données nécessaires
- Facilite la sérialisation (JSON, etc.)

Différence Entity vs DTO:
- Entity (Domain): Objet métier avec comportements et validations
- DTO: Simple conteneur de données pour transfert entre couches

Example:
    # Domain Entity (avec validation)
    job_offer = JobOffer(text="...")  # Valide que text >= 50 caractères

    # DTO (juste data)
    dto = JobOfferDTO(text="...")  # Pas de validation, juste transfert
"""

from app.application.dtos.document_dto import DocumentDTO
from app.application.dtos.generation_result_dto import GenerationResultDTO
from app.application.dtos.job_analysis_dto import JobAnalysisDTO
from app.application.dtos.job_offer_dto import JobOfferDTO
from app.application.dtos.trace_context_dto import TraceContextDTO

__all__ = [
    "JobOfferDTO",
    "JobAnalysisDTO",
    "DocumentDTO",
    "GenerationResultDTO",
    "TraceContextDTO",
]
