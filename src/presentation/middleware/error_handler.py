"""
Global Error Handler Middleware
Maneja todas las excepciones y retorna responses consistentes
"""
import structlog
from domain.exceptions.payment_errors import PaymentFailedError
from domain.exceptions.reservation_errors import (
    ReservationError,
    ReservationNotFoundError,
)
from domain.exceptions.supplier_errors import SupplierError
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
