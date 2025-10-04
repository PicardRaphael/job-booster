"""API router aggregation."""

from fastapi import APIRouter

from app.api import generation, health

# Aggregate all routers
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(generation.router)

__all__ = ["api_router"]
