"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.services.embeddings import get_embedding_service
from app.services.qdrant_service import get_qdrant_service
from app.services.reranker import get_reranker_service

# Setup logging
setup_logging(debug=settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("starting_application", version=settings.api_version)

    # Initialize services
    logger.info("initializing_services")
    get_embedding_service()
    get_reranker_service()

    # Ensure Qdrant collection exists
    qdrant = get_qdrant_service()
    qdrant.ensure_collection()

    logger.info("application_started")

    yield

    # Shutdown
    logger.info("shutting_down_application")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
