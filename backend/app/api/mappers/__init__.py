"""
API Mappers.

Presentation Layer - Clean Architecture

Mappers pour convertir entre API models et Application DTOs.

Pourquoi des mappers?
- Decoupler l'API des DTOs application
- Si on change l'API REST, on ne touche pas aux DTOs
- Si on change les DTOs, on ne touche pas a l'API
- Respecte le Dependency Inversion Principle
"""

from app.api.mappers.generation_mapper import GenerationMapper

__all__ = ["GenerationMapper"]
