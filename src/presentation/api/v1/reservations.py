"""
Reservations Router
Endpoints para crear y consultar reservas
"""
from datetime import UTC, datetime
from typing import Annotated, cast

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.application.dto.reservation_dto import (
    CreateReservationDTO,
    GetReservationDTO,
    ListReservationsDTO,
)
from src.application.ports.unit_of_work import UnitOfWork
from src.application.use_cases.reservations.create_reservation import CreateReservationUseCase
from src.application.use_cases.reservations.get_reservation import GetReservationUseCase
from src.application.use_cases.reservations.list_reservations import ListReservationsUseCase
from src.domain.exceptions.payment_errors import PaymentFailedError
from src.domain.exceptions.reservation_errors import ReservationCreationError
from src.domain.exceptions.supplier_errors import SupplierConfirmationError
from src.infrastructure.documents.receipt_generator import WeasyPrintReceiptGenerator
from src.infrastructure.external.payments.stripe_client import StripePaymentGateway
from src.infrastructure.external.suppliers.supplier_factory import SupplierFactory
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.schemas.reservation_schemas import (
    CreateReservationRequest,
    ErrorResponse,
    ReservationDetailResponse,
    ReservationResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/reservations", tags=["Reservations"])


# ============================================
# DEPENDENCIES
# ============================================

class ReservationDependencies:
    """Contenedor de dependencias para creación de reservas"""
    def __init__(self):
        self.uow = SQLAlchemyUnitOfWork()
        self.payment_gateway = StripePaymentGateway()
        self.supplier_factory = SupplierFactory()
        self.receipt_generator = WeasyPrintReceiptGenerator()

async def get_reservation_dependencies() -> ReservationDependencies:
    """Dependency factory"""
    return ReservationDependencies()


async def get_get_reservation_use_case() -> GetReservationUseCase:
    """Dependency para GetReservationUseCase"""
    uow = SQLAlchemyUnitOfWork()
    return GetReservationUseCase(uow=cast(UnitOfWork, uow))


async def get_list_reservations_use_case() -> ListReservationsUseCase:
    """Dependency para ListReservationsUseCase"""
    uow = SQLAlchemyUnitOfWork()
    return ListReservationsUseCase(uow=cast(UnitOfWork, uow))


# ============================================
# ENDPOINTS
# ============================================

@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Reservation created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        402: {"model": ErrorResponse, "description": "Payment failed"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        503: {"model": ErrorResponse, "description": "Supplier error"},
    },
    summary="Create a new reservation",
    description="""
    Create a new car rental reservation with payment processing.
    Flow:
    1. Validate request data
    2. Generate unique reservation code
    3. Process payment with Stripe
    4. Confirm with supplier
    5. Generate receipt PDF
    6. Return reservation details
    """,
)
async def create_reservation(
    request: CreateReservationRequest,
    deps: Annotated[ReservationDependencies, Depends(get_reservation_dependencies)],
    x_idempotency_key: Annotated[str | None, Header()] = None,
) -> ReservationResponse:
    """
    Create a new reservation

    **Idempotency:** Use X-Idempotency-Key header to prevent duplicate requests
    """
    logger.info(
        "create_reservation_request",
        supplier_id=request.supplier_id,
        pickup_datetime=request.pickup_datetime.isoformat(),
        idempotency_key=x_idempotency_key,
    )

    # TODO: Implementar idempotency check aquí si x_idempotency_key está presente

    try:
        # Obtener supplier gateway específico para este request
        supplier_gateway = await deps.supplier_factory.get_supplier(request.supplier_id)

        # Instanciar caso de uso con el supplier correcto
        use_case = CreateReservationUseCase(
            uow=cast(UnitOfWork, deps.uow),
            supplier_gateway=supplier_gateway,
            payment_gateway=deps.payment_gateway,
            receipt_generator=deps.receipt_generator,
        )

        # Convertir request a DTO
        dto = CreateReservationDTO.from_request(request) # type: ignore

        # Ejecutar caso de uso
        result = await use_case.execute(dto)

        # Mapear resultado a response
        return ReservationResponse(
            reservation_id=result.reservation_id,
            reservation_code=result.reservation_code,
            supplier_reservation_code=result.supplier_reservation_code,
            status=result.status,
            payment_status=result.payment_status,
            total_amount=result.total_amount,
            currency_code=result.currency_code,
            receipt_url=result.receipt_url,
            created_at=datetime.now(UTC),
        )

    except PaymentFailedError as e:
        logger.error("payment_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "PaymentFailed",
                "message": str(e),
                "code": "PAYMENT_FAILED"
            }
        )
    except SupplierConfirmationError as e:
        logger.error("supplier_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "SupplierError",
                "message": str(e),
                "code": "SUPPLIER_ERROR"
            }
        )
    except (ReservationCreationError, ValueError) as e:
        logger.error("reservation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ReservationError",
                "message": str(e),
                "code": "BAD_REQUEST"
            }
        )


@router.get(
    "/{reservation_code}",
    response_model=ReservationDetailResponse,
    responses={
        200: {"description": "Reservation details"},
        404: {"model": ErrorResponse, "description": "Reservation not found"},
    },
    summary="Get reservation by code",
    description="Retrieve detailed information about a reservation using its code",
)
async def get_reservation_by_code(
    reservation_code: str,
    use_case: Annotated[GetReservationUseCase, Depends(get_get_reservation_use_case)],
) -> ReservationDetailResponse:
    """Get reservation details by reservation code"""

    logger.info("get_reservation_request", reservation_code=reservation_code)

    dto = GetReservationDTO(reservation_code=reservation_code)
    reservation = await use_case.execute(dto)

    if reservation.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Reservation ID is missing",
                "code": "INTERNAL_ERROR"
            }
        )

    # Obtener driver principal
    driver_name = None
    driver_email = None
    for driver in reservation.drivers:
        if driver.is_primary_driver:
            driver_name = driver.full_name
            driver_email = driver.email
            break

    return ReservationDetailResponse(
        reservation_id=reservation.id,
        reservation_code=reservation.reservation_code,
        supplier_reservation_code=reservation.supplier_reservation_code,
        status=reservation.status.value,
        payment_status=reservation.payment_status.value,
        pickup_datetime=reservation.pickup_datetime,
        dropoff_datetime=reservation.dropoff_datetime,
        rental_days=reservation.rental_days,
        total_amount=reservation.public_price_total,
        currency_code=reservation.currency_code,
        supplier_name=reservation.supplier_name_snapshot,
        pickup_office_name=reservation.pickup_office_name_snapshot,
        dropoff_office_name=reservation.dropoff_office_name_snapshot,
        car_category_name=reservation.car_category_name_snapshot,
        acriss_code=reservation.car_acriss_code_snapshot,
        driver_name=driver_name,
        driver_email=driver_email,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at,
    )


@router.get(
    "",
    response_model=list[ReservationDetailResponse],
    summary="List reservations",
    description="List reservations with optional filters",
)
async def list_reservations(
    use_case: Annotated[ListReservationsUseCase, Depends(get_list_reservations_use_case)],
    customer_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ReservationDetailResponse]:
    """
    List reservations
    **Filters:**
    - customer_id: Filter by customer ID
    - limit: Number of results (max 100)
    - offset: Pagination offset
    """

    logger.info(
        "list_reservations_request",
        customer_id=customer_id,
        limit=limit,
        offset=offset,
    )

    dto = ListReservationsDTO(
        customer_id=customer_id,
        limit=min(limit, 100),
        offset=offset,
    )

    reservations = await use_case.execute(dto)

    results: list[ReservationDetailResponse] = []
    for reservation in reservations:
        if reservation.id is None:
            continue  # Skip reservations without ID

        # Obtener driver principal
        driver_name = None
        driver_email = None
        for driver in reservation.drivers:
            if driver.is_primary_driver:
                driver_name = driver.full_name
                driver_email = driver.email
                break

        results.append(ReservationDetailResponse(
            reservation_id=reservation.id,
            reservation_code=reservation.reservation_code,
            supplier_reservation_code=reservation.supplier_reservation_code,
            status=reservation.status.value,
            payment_status=reservation.payment_status.value,
            pickup_datetime=reservation.pickup_datetime,
            dropoff_datetime=reservation.dropoff_datetime,
            rental_days=reservation.rental_days,
            total_amount=reservation.public_price_total,
            currency_code=reservation.currency_code,
            supplier_name=reservation.supplier_name_snapshot,
            pickup_office_name=reservation.pickup_office_name_snapshot,
            dropoff_office_name=reservation.dropoff_office_name_snapshot,
            car_category_name=reservation.car_category_name_snapshot,
            acriss_code=reservation.car_acriss_code_snapshot,
            driver_name=driver_name,
            driver_email=driver_email,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
        ))

    return results
