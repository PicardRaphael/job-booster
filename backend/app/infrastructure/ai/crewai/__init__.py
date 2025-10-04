"""
CrewAI Infrastructure.

Infrastructure Layer - Clean Architecture

Builders et adapters pour CrewAI.

Pourquoi dans Infrastructure?
- CrewAI est un détail d'implémentation
- On pourrait remplacer par Autogen, LangGraph, etc.
- Le Domain ne doit pas savoir qu'on utilise CrewAI

Modules:
- agent_builder: Builder pattern pour créer des agents CrewAI
- crew_builder: Builder pattern pour créer des crews CrewAI
"""

from app.infrastructure.ai.crewai.agent_builder import AgentBuilder
from app.infrastructure.ai.crewai.crew_builder import CrewBuilder

__all__ = ["AgentBuilder", "CrewBuilder"]
