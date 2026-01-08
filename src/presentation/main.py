"""
FastAPI Application Entry Point
Main configuration for Car Rental Reservations API
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.presentation.api.v1 import reservations, availability
from src.presentation.middleware.error_handler import setup_exception_handlers

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup
    logger.info("application_starting", env="production")
    yield
    # Shutdown
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """
    Factory function to create FastAPI application
    """
    app = FastAPI(
        title="Car Rental Reservations API",
        description="Global car rental reservation system with high concurrency support",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Register routers
    app.include_router(
        reservations.router,
        prefix="/api/v1/reservations",
        tags=["Reservations"]
    )
    app.include_router(
        availability.router,
        prefix="/api/v1/availability",
        tags=["Availability"]
    )

    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint"""
        return {
            "service": "Car Rental Reservations API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "presentation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
