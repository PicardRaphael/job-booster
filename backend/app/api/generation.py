"""
Content Generation Endpoints.

Presentation Layer - Clean Architecture

Endpoints FastAPI pour la génération de contenu.
Responsabilité: Adapter HTTP ↔ Application layer.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.mappers import GenerationMapper
from app.core.container import get_container
from app.core.logging import get_logger
from app.domain.exceptions import NoDatabaseDocumentsError
from app.models import GenerateRequest, GenerateResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("", response_model=GenerateResponse, status_code=status.HTTP_200_OK)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """
    Génère du contenu de candidature (email, LinkedIn, lettre).

    Clean Architecture Flow:
    1. API reçoit HTTP request
    2. Mapper convertit Request → Command
    3. Orchestrator exécute le workflow complet
    4. Mapper convertit ResultDTO → Response
    5. API retourne HTTP response

    Args:
        request: GenerateRequest avec job_offer et output_type

    Returns:
        GenerateResponse avec contenu généré et sources

    Raises:
        HTTPException 404: Aucun document trouvé dans la base
        HTTPException 500: Erreur lors de la génération

    Example:
        POST /generate
        {
            "job_offer": "Développeur Python...",
            "output_type": "email"
        }
    """
    logger.info(
        "generate_request_received",
        output_type=request.output_type,
        offer_length=len(request.job_offer),
    )

    try:
        # Étape 1: Get orchestrator from DI container
        container = get_container()
        orchestrator = container.generate_application_orchestrator()

        # Étape 2: Map HTTP request → Application command
        command = GenerationMapper.request_to_command(request)

        # Étape 3: Execute orchestrator (business logic)
        result = orchestrator.execute(command)

        # Étape 4: Map Application result → HTTP response
        response = GenerationMapper.result_to_response(result)

        logger.info(
            "generation_completed",
            output_type=request.output_type,
            output_length=len(response.output),
            sources_count=len(response.sources),
        )

        return response

    except NoDatabaseDocumentsError as e:
        # Business exception → HTTP 404
        logger.warning("no_database_documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
    except Exception as e:
        # Unexpected error → HTTP 500
        logger.error("generation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}",
        )
