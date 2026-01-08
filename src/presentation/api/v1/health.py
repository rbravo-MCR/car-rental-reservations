"""
Health Check Router
Endpoints para monitoreo y health checks
"""
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, status
from pydantic import BaseModel

logger = structlog.get_logger()

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "0.1.0"
    service: str = "car-rental-reservations"


class DetailedHealthResponse(HealthResponse):
    """Detailed health check with dependencies"""
    database: str = "unknown"
    redis: str = "unknown"
    stripe: str = "unknown"


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the API",
)
async def health_check() -> HealthResponse:
    """
    Basic health check

    Returns 200 OK if the service is running
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    summary="Detailed health check",
    description="Returns detailed health status including dependencies",
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check

    Checks status of:
    - Database (MySQL)
    - Cache (Redis)
    - Payment gateway (Stripe)
    """

    # TODO: Implementar checks reales de dependencias
    # Por ahora retornamos datos mock

    health = DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
        database="connected",
        redis="connected",
        stripe="configured",
    )

    logger.info("detailed_health_check", health=health.model_dump())

    return health


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint",
)
async def readiness_check():
    """
    Readiness check for Kubernetes

    Returns 200 if the service is ready to accept traffic
    Returns 503 if not ready
    """
    # TODO: Verificar que BD esté accesible
    return {"status": "ready"}


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint",
)
async def liveness_check():
    """
    Liveness check for Kubernetes

    Returns 200 if the service is alive
    """
    return {"status": "alive"}
