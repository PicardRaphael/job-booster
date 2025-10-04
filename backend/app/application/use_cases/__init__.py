"""
Use Cases - Application Layer.

Application Layer - Clean Architecture

Les use cases représentent les cas d'usage métier de l'application.
Ils orchestrent les services domain pour réaliser des actions métier.

Architecture:
- Use cases atomiques: Un seul objectif (SRP)
- Orchestrateurs: Composent plusieurs use cases

Use Cases Atomiques:
- AnalyzeJobOfferUseCase: Analyser une offre
- SearchDocumentsUseCase: Chercher dans Qdrant
- RerankDocumentsUseCase: Reranker les résultats
- GenerateEmailUseCase: Générer un email
- GenerateLinkedInUseCase: Générer un post LinkedIn
- GenerateCoverLetterUseCase: Générer une lettre
- TraceGenerationUseCase: Créer trace observability

Orchestrateurs:
- GenerateApplicationOrchestrator: Compose tous les use cases
"""

# Use cases atomiques
from app.application.use_cases.analyze_job_offer import AnalyzeJobOfferUseCase
from app.application.use_cases.generate_cover_letter import GenerateCoverLetterUseCase
from app.application.use_cases.generate_email import GenerateEmailUseCase
from app.application.use_cases.generate_linkedin import GenerateLinkedInUseCase
from app.application.use_cases.rerank_documents import RerankDocumentsUseCase
from app.application.use_cases.search_documents import SearchDocumentsUseCase
from app.application.use_cases.trace_generation import TraceGenerationUseCase

# Legacy (à supprimer après migration)
from app.application.use_cases.generate_application_content import (
    GenerateApplicationContentUseCase,
)

__all__ = [
    # Use cases atomiques
    "AnalyzeJobOfferUseCase",
    "SearchDocumentsUseCase",
    "RerankDocumentsUseCase",
    "GenerateEmailUseCase",
    "GenerateLinkedInUseCase",
    "GenerateCoverLetterUseCase",
    "TraceGenerationUseCase",
    # Legacy
    "GenerateApplicationContentUseCase",
]
