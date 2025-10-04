"""
Orchestrators - Application Layer.

Application Layer - Clean Architecture

Les orchestrateurs composent plusieurs use cases pour réaliser
des workflows complexes.

Différence Orchestrateur vs Use Case:
- Use Case: Action atomique (1 responsabilité)
- Orchestrateur: Compose plusieurs use cases (workflow)

Example:
    # Use case atomique
    analysis = analyze_use_case.execute(command)

    # Orchestrateur (compose 4 use cases)
    result = orchestrator.execute(command)
    # → Appelle analyze, search, rerank, generate
"""

from app.application.orchestrators.generate_application_orchestrator import (
    GenerateApplicationOrchestrator,
)

__all__ = ["GenerateApplicationOrchestrator"]
