"""
Availability Router
Endpoints para búsqueda de disponibilidad de vehículos
"""
from typing import Annotated, cast

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dto.availability_dto import AvailabilitySearchDTO
from src.application.ports.unit_of_work import UnitOfWork
from src.application.use_cases.availability.search_availability import SearchAvailabilityUseCase
from src.infrastructure.external.suppliers.supplier_factory import SupplierFactory
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.schemas.availability_schemas import (
    AvailabilitySearchRequest,
    VehicleAvailabilityResponse,
)
from src.presentation.schemas.reservation_schemas import ErrorResponse

logger = structlog.get_logger()

router = APIRouter()


# ============================================
# DEPENDENCIES
# ============================================

async def get_search_availability_use_case() -> SearchAvailabilityUseCase:
    """Dependency para SearchAvailabilityUseCase"""
    uow = SQLAlchemyUnitOfWork()
    supplier_factory = SupplierFactory()

    # Por ahora usamos Localiza (supplier_id=1) como default
    # TODO: Hacer esto dinámico según el request
    supplier_gateway = await supplier_factory.get_supplier(supplier_id=1)

    return SearchAvailabilityUseCase(
        uow=cast(UnitOfWork, uow),
        supplier_gateway=supplier_gateway,
    )


# ============================================
# ENDPOINTS
# ============================================

@router.post(
    "",
    response_model=list[VehicleAvailabilityResponse],
    responses={
        200: {"description": "Available vehicles found"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "No vehicles available"},
        503: {"model": ErrorResponse, "description": "Supplier unavailable"},
    },
    summary="Search vehicle availability",
    description="""
    Search for available vehicles based on pickup/dropoff locations and dates.

    Returns a list of available vehicles from one or all suppliers with pricing information.
    """,
)
async def search_availability(
    request: AvailabilitySearchRequest,
    use_case: Annotated[SearchAvailabilityUseCase, Depends(get_search_availability_use_case)],
) -> list[VehicleAvailabilityResponse]:
    """
    Search for available vehicles

    **Parameters:**
    - pickup_office_id: Pickup office ID
    - dropoff_office_id: Dropoff office ID
    - pickup_datetime: Pickup date and time (ISO 8601)
    - dropoff_datetime: Dropoff date and time (ISO 8601)
    - driver_age: Driver age (optional, default 30)
    - supplier_id: Specific supplier to search (optional, searches all if not provided)
    """

    try:
        logger.info(
            "search_availability_request",
            pickup_office=request.pickup_office_id,
            dropoff_office=request.dropoff_office_id,
            pickup_datetime=request.pickup_datetime.isoformat(),
            dropoff_datetime=request.dropoff_datetime.isoformat(),
            supplier_id=request.supplier_id,
        )

        # Convertir request a DTO
        dto = AvailabilitySearchDTO(
            pickup_office_id=request.pickup_office_id,
            dropoff_office_id=request.dropoff_office_id,
            pickup_datetime=request.pickup_datetime,
            dropoff_datetime=request.dropoff_datetime,
            driver_age=request.driver_age or 30,
            supplier_id=request.supplier_id,
        )

        # Ejecutar caso de uso
        results = await use_case.execute(dto)

        if not results:
            logger.warning("no_vehicles_available", filters=dto)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NoVehiclesAvailable",
                    "message": "No vehicles available for the selected dates and location",
                    "code": "NO_VEHICLES_AVAILABLE",
                },
            )

        # Mapear resultados a response
        response = [
            VehicleAvailabilityResponse(
                supplier_id=vehicle.supplier_id,
                supplier_name=vehicle.supplier_name,
                vehicle_id=vehicle.vehicle_id,
                vehicle_name=vehicle.vehicle_name,
                acriss_code=vehicle.acriss_code,
                car_category_name=vehicle.car_category_name,
                total_price=vehicle.total_price,
                daily_rate=vehicle.daily_rate,
                currency_code=vehicle.currency_code,
                doors=vehicle.doors,
                seats=vehicle.seats,
                transmission=vehicle.transmission,
                air_conditioning=vehicle.air_conditioning,
            )
            for vehicle in results
        ]

        logger.info("search_availability_success", count=len(response))
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        logger.error("validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "code": "VALIDATION_ERROR",
            },
        )

    except Exception as e:
        logger.error("unexpected_error_searching_availability", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "An unexpected error occurred while searching for vehicles",
                "code": "INTERNAL_ERROR",
            },
        )


@router.get(
    "/health",
    summary="Availability service health check",
    description="Check if the availability service is operational",
)
async def availability_health():
    """Health check endpoint for availability service"""
    return {
        "service": "availability",
        "status": "healthy",
        "message": "Availability search service is operational"
    }
