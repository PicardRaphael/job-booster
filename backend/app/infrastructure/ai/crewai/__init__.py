"""
CrewAI Infrastructure.

Infrastructure Layer - Clean Architecture

Builders et adapters pour CrewAI.

Pourquoi dans Infrastructure?
- CrewAI est un detail d'implementation
- On pourrait remplacer par Autogen, LangGraph, etc.
- Le Domain ne doit pas savoir qu'on utilise CrewAI

Modules:
- agent_builder: Builder pattern pour creer des agents CrewAI
- crew_builder: Builder pattern pour creer des crews CrewAI
- content_writer_service: Service composite pour tous les writers
- email_writer_adapter: Adapter pour generer des emails
- linkedin_writer_adapter: Adapter pour generer des messages LinkedIn
- letter_writer_adapter: Adapter pour generer des lettres
"""

from app.infrastructure.ai.crewai.agent_builder import AgentBuilder
from app.infrastructure.ai.crewai.crew_builder import CrewBuilder
from app.infrastructure.ai.crewai.content_writer_service import CrewAIContentWriterService
from app.infrastructure.ai.crewai.email_writer_adapter import EmailWriterAdapter
from app.infrastructure.ai.crewai.linkedin_writer_adapter import LinkedInWriterAdapter
from app.infrastructure.ai.crewai.letter_writer_adapter import LetterWriterAdapter

__all__ = [
    "AgentBuilder",
    "CrewBuilder",
    "CrewAIContentWriterService",
    "EmailWriterAdapter",
    "LinkedInWriterAdapter",
    "LetterWriterAdapter",
]
