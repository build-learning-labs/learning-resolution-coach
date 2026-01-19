"""Health check routes."""

from fastapi import APIRouter

from shared.schemas import HealthCheck


router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        service="gateway",
        version="0.1.0",
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Add database connectivity check here
    return {"status": "ready"}
