"""
Reservation DTOs
Input/Output para casos de uso de reservas
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.presentation.schemas.reservation_schemas import CreateReservationRequest


@dataclass
class DriverDTO:
    """DTO para datos del conductor"""
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str | None = None
    driver_license_number: str | None = None
    driver_license_country: str | None = None


@dataclass
class CreateReservationDTO:
    """DTO para crear reserva"""

    # Driver info
    driver: DriverDTO

    # Vehicle selection
    supplier_id: int
    vehicle_id: int  # supplier_car_product_id
    acriss_code: str
    car_category_id: int

    # Pickup/Dropoff
    pickup_office_id: int
    pickup_office_code: str
    pickup_datetime: datetime
    dropoff_office_id: int
    dropoff_office_code: str
    dropoff_datetime: datetime
    rental_days: int

    # Pricing
    price: Decimal
    currency_code: str

    # Payment
    payment_method_id: str

    # Optional
    app_customer_id: int | None = None
    sales_channel_id: int = 1

from src.presentation.schemas.reservation_schemas import CreateReservationRequest

...

    @classmethod
    def from_request(cls, request: CreateReservationRequest) -> "CreateReservationDTO":
        """Crear DTO desde request de API"""
        from src.domain.services.pricing_calculator import PricingCalculator

        rental_days = PricingCalculator.calculate_rental_days(
            request.pickup_datetime,
            request.dropoff_datetime
        )

        return cls(
            driver=DriverDTO(
                first_name=request.driver.first_name,
                last_name=request.driver.last_name,
                email=request.driver.email,
                phone=request.driver.phone,
            ),
            supplier_id=request.supplier_id,
            vehicle_id=request.vehicle_id,
            acriss_code=request.acriss_code,
            car_category_id=0,  # Se obtendrá del vehicle
            pickup_office_id=request.pickup_office_id,
            pickup_office_code="",  # Se obtendrá de DB
            pickup_datetime=request.pickup_datetime,
            dropoff_office_id=request.dropoff_office_id,
            dropoff_office_code="",  # Se obtendrá de DB
            dropoff_datetime=request.dropoff_datetime,
            rental_days=rental_days,
            price=request.price,
            currency_code=request.currency_code,
            payment_method_id=request.payment_method_id,
            sales_channel_id=1,
        )


@dataclass
class ReservationResultDTO:
    """DTO para resultado de operación de reserva"""

    reservation_id: int
    reservation_code: str
    supplier_reservation_code: str | None
    status: str
    payment_status: str
    total_amount: Decimal
    currency_code: str
    receipt_url: str | None = None
    created_at: datetime | None = None


@dataclass
class GetReservationDTO:
    """DTO para consultar reserva"""

    reservation_id: int | None = None
    reservation_code: str | None = None


@dataclass
class ListReservationsDTO:
    """DTO para listar reservas"""

    customer_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    limit: int = 50
    offset: int = 0
