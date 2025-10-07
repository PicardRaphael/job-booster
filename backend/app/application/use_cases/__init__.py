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
- GenerateLinkedInUseCase: Générer un message privé LinkedIn
- GenerateCoverLetterUseCase: Générer une lettre

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

__all__ = [
    "AnalyzeJobOfferUseCase",
    "SearchDocumentsUseCase",
    "RerankDocumentsUseCase",
    "GenerateEmailUseCase",
    "GenerateLinkedInUseCase",
    "GenerateCoverLetterUseCase",
]
