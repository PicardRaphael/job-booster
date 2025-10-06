"""Health check and system status endpoints."""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import get_logger
from app.services.embeddings import get_embedding_service
from app.services.langfuse_service import get_langfuse_service
from app.services.qdrant_service import get_qdrant_service
from app.services.reranker import get_reranker_service

logger = get_logger(__name__)
router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Quick health check endpoint.

    Returns:
        Simple health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status")
async def detailed_status() -> Dict[str, Any]:
    """
    Detailed system status with all services.

    Returns:
        Comprehensive status of all components
    """
    services = {}
    overall_status = "healthy"

    # Check Qdrant
    try:
        qdrant = get_qdrant_service()
        collections = qdrant.client.get_collections()
        services["qdrant"] = {
            "status": "healthy",
            "url": settings.qdrant_url,
            "collections": len(collections.collections),
            "target_collection": settings.qdrant_collection,
        }
    except Exception as e:
        logger.error("qdrant_health_check_failed", error=str(e))
        services["qdrant"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check Langfuse
    try:
        get_langfuse_service()
        services["langfuse"] = {
            "status": "healthy",
            "host": settings.langfuse_host,
        }
    except Exception as e:
        logger.error("langfuse_health_check_failed", error=str(e))
        services["langfuse"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check Embedding Service
    try:
        embedding_service = get_embedding_service()
        services["embeddings"] = {
            "status": "healthy",
            "model": settings.embedding_model,
            "dimension": embedding_service.get_dimension(),
        }
    except Exception as e:
        logger.error("embeddings_health_check_failed", error=str(e))
        services["embeddings"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check Reranker Service
    try:
        get_reranker_service()
        services["reranker"] = {
            "status": "healthy",
            "model": settings.reranker_model,
        }
    except Exception as e:
        logger.error("reranker_health_check_failed", error=str(e))
        services["reranker"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check LLM Configuration
    services["llm"] = {
        "status": "healthy",
        "providers": {
            "openai": {
                "configured": bool(settings.openai_api_key),
                "model": settings.openai_model,
            },
            "google": {
                "configured": bool(settings.google_api_key),
                "model": settings.gemini_model,
            },
        },
    }

    return {
        "status": overall_status,
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat(),
        "services": services,
    }


@router.get("/info")
async def system_info() -> Dict[str, Any]:
    """
    System information and configuration.

    Returns:
        System configuration details
    """
    return {
        "api": {
            "title": settings.api_title,
            "version": settings.api_version,
            "debug": settings.debug,
        },
        "models": {
            "embeddings": settings.embedding_model,
            "reranker": settings.reranker_model,
            "llm": {
                "openai": settings.openai_model,
                "google": settings.gemini_model,
            },
        },
        "storage": {
            "qdrant_cluster": settings.qdrant_cluster,
            "qdrant_collection": settings.qdrant_collection,
        },
        "chunking": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
        },
    }


@router.get("/ready")
async def readiness_probe() -> Dict[str, str]:
    """
    Kubernetes readiness probe.

    Returns:
        Readiness status
    """
    try:
        # Check critical services
        qdrant = get_qdrant_service()
        qdrant.client.get_collections()

        get_embedding_service()

        return {"status": "ready"}
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe.

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
