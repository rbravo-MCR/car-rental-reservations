"""
Global Error Handler Middleware
Maneja todas las excepciones y retorna responses consistentes
"""
from typing import TYPE_CHECKING

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions.payment_errors import PaymentFailedError
from src.domain.exceptions.reservation_errors import (
    ReservationError,
    ReservationNotFoundError,
)
from src.domain.exceptions.supplier_errors import SupplierError

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = structlog.get_logger()


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware para capturar excepciones globalmente
    """
    try:
        return await call_next(request)
    except Exception as e:
        return handle_exception(e, request)


def handle_exception(exc: Exception, request: Request) -> JSONResponse:
    """
    Convertir excepciones a JSONResponse consistente
    """
    # Log del error
    logger.error(
        "request_error",
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
    )

    # Excepciones de dominio
    if isinstance(exc, ReservationNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "ReservationNotFound",
                "message": str(exc),
                "code": "RESERVATION_NOT_FOUND",
            }
        )

    if isinstance(exc, PaymentFailedError):
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "error": "PaymentFailed",
                "message": str(exc),
                "code": "PAYMENT_FAILED",
            }
        )

    if isinstance(exc, SupplierError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "SupplierError",
                "message": str(exc),
                "code": "SUPPLIER_ERROR",
            }
        )

    if isinstance(exc, ReservationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ReservationError",
                "message": str(exc),
                "code": getattr(exc, 'code', 'RESERVATION_ERROR'),
            }
        )

    # Validación de Pydantic
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            }
        )

    # Excepciones no manejadas
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configure global exception handlers for the FastAPI application

    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(ReservationNotFoundError)
    async def reservation_not_found_handler(request: Request, exc: ReservationNotFoundError):
        return handle_exception(exc, request)

    @app.exception_handler(PaymentFailedError)
    async def payment_failed_handler(request: Request, exc: PaymentFailedError):
        return handle_exception(exc, request)

    @app.exception_handler(SupplierError)
    async def supplier_error_handler(request: Request, exc: SupplierError):
        return handle_exception(exc, request)

    @app.exception_handler(ReservationError)
    async def reservation_error_handler(request: Request, exc: ReservationError):
        return handle_exception(exc, request)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return handle_exception(exc, request)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return handle_exception(exc, request)

    logger.info("exception_handlers_configured")
