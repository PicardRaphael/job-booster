"""
Generation Mapper.

Presentation Layer - Clean Architecture

Mapper pour convertir entre API models et Application DTOs.
"""

from app.application.commands import GenerateApplicationCommand
from app.application.dtos import GenerationResultDTO, JobOfferDTO
from app.models import GenerateRequest, GenerateResponse, SourceDTO


class GenerationMapper:
    """
    Mapper pour les endpoints de g�n�ration.

    Responsabilit� (SRP):
    - Convertir Request � Command (API � Application)
    - Convertir ResultDTO � Response (Application � API)
    - Une seule raison de changer: si le format change

    Pattern Mapper:
    - D�couple l'API des DTOs application
    - Facilite les changements d'API sans toucher au m�tier
    - Suit le principe de s�paration des couches

    Example:
        >>> request = GenerateRequest(job_offer="...", output_type="email")
        >>> command = GenerationMapper.request_to_command(request)
        >>> # ... execute use case ...
        >>> response = GenerationMapper.result_to_response(result_dto)
    """

    @staticmethod
    def request_to_command(request: GenerateRequest) -> GenerateApplicationCommand:
        """
        Convertit API Request � Application Command.

        Args:
            request: GenerateRequest depuis FastAPI

        Returns:
            GenerateApplicationCommand pour l'orchestrateur

        Example:
            >>> request = GenerateRequest(
            ...     job_offer="D�veloppeur Python...",
            ...     output_type=OutputType.EMAIL
            ... )
            >>> command = GenerationMapper.request_to_command(request)
            >>> print(command.content_type)
            "email"
        """
        return GenerateApplicationCommand(
            job_offer=JobOfferDTO(text=request.get_job_offer_text()),
            content_type=request.output_type,
        )

    @staticmethod
    def result_to_response(result: GenerationResultDTO) -> GenerateResponse:
        """
        Convertit Application ResultDTO � API Response.

        Args:
            result: GenerationResultDTO depuis l'orchestrateur

        Returns:
            GenerateResponse pour FastAPI

        Example:
            >>> result = GenerationResultDTO(
            ...     content="Email g�n�r�...",
            ...     content_type="email",
            ...     sources=[...],
            ...     trace_id="langfuse-123"
            ... )
            >>> response = GenerationMapper.result_to_response(result)
            >>> print(response.output)
            "Email g�n�r�..."
        """
        # Convertir DocumentDTO � SourceDTO (API model)
        sources = [
            SourceDTO(
                id=doc.id,
                text=doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                score=doc.rerank_score if doc.rerank_score else doc.score,
                source=doc.source,
            )
            for doc in result.sources
        ]

        return GenerateResponse(
            output=result.content,
            output_type=result.content_type,
            sources=sources,
            trace_id=result.trace_id,
        )
