"""
Commands (CQRS Pattern).

Application Layer - Clean Architecture

Pourquoi des Commands?
- Pattern CQRS (Command Query Responsibility Segregation)
- Rend les use cases explicites et testables
- Facilite l'ajout de middlewares (logging, validation, auth)
- Chaque command = intention claire de l'utilisateur

Command vs DTO:
- Command: Représente une action ("AnalyzeJobOffer", "SearchDocuments")
- DTO: Juste data sans intention ("JobOfferDTO", "DocumentDTO")

Example:
    # Command = intention
    command = AnalyzeJobOfferCommand(job_offer=dto)
    result = use_case.execute(command)  # ← Execute une action
"""

from app.application.commands.analyze_job_offer_command import AnalyzeJobOfferCommand
from app.application.commands.generate_application_command import (
    GenerateApplicationCommand,
)
from app.application.commands.generate_content_command import GenerateContentCommand
from app.application.commands.rerank_documents_command import RerankDocumentsCommand
from app.application.commands.search_documents_command import SearchDocumentsCommand

__all__ = [
    "AnalyzeJobOfferCommand",
    "SearchDocumentsCommand",
    "RerankDocumentsCommand",
    "GenerateContentCommand",
    "GenerateApplicationCommand",
]
