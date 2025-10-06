"""
API Response Models.

Pydantic models pour les réponses HTTP.
"""

from typing import List, Literal

from pydantic import BaseModel, Field


class SourceDTO(BaseModel):
    """Source document utilisée pour la génération."""

    id: str = Field(..., description="ID unique de la source")
    text: str = Field(..., description="Texte extrait de la source")
    source: str = Field(..., description="Nom du fichier source")
    score: float = Field(..., description="Score de pertinence (0-1)")


class GenerateResponse(BaseModel):
    """Réponse de génération de contenu."""

    output: str = Field(..., description="Contenu généré")
    output_type: Literal["email", "linkedin", "letter"] = Field(
        ..., description="Type de contenu généré"
    )
    sources: List[SourceDTO] = Field(..., description="Sources utilisées")
    trace_id: str = Field(..., description="ID de traçabilité")
