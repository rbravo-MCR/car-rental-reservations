"""
Pydantic Schemas for Reservation endpoints
Request/Response models
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator


class DriverRequest(BaseModel):
    """Schema para datos del conductor"""
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=50)
    date_of_birth: str | None = None
    driver_license_number: str | None = None
    driver_license_country: str | None = None


class CreateReservationRequest(BaseModel):
    """Schema para crear reserva"""

    # Driver
    driver: DriverRequest

    # Vehicle
    supplier_id: int = Field(..., gt=0)
    vehicle_id: int = Field(..., gt=0, description="supplier_car_product_id")
    acriss_code: str = Field(..., min_length=4, max_length=10)

    # Pickup/Dropoff
    pickup_office_id: int = Field(..., gt=0)
    pickup_datetime: datetime
    dropoff_office_id: int = Field(..., gt=0)
    dropoff_datetime: datetime

    # Pricing
    price: Decimal = Field(..., gt=0, decimal_places=2)
    currency_code: str = Field(..., min_length=3, max_length=3)

    # Payment
    payment_method_id: str = Field(..., description="Stripe payment method ID")

    # Optional
    app_customer_id: int | None = None

    @field_validator('pickup_datetime', 'dropoff_datetime')
    @classmethod
    def validate_datetime(cls, v):
        """Validar que fechas sean futuras"""
        if v < datetime.utcnow():
            raise ValueError('Datetime must be in the future')
        return v

    @field_validator('dropoff_datetime')
    @classmethod
    def validate_dropoff_after_pickup(cls, v, info):
        """Validar que dropoff sea después de pickup"""
        if 'pickup_datetime' in info.data:
            if v <= info.data['pickup_datetime']:
                raise ValueError('Dropoff must be after pickup')
        return v

    @field_validator('currency_code')
    @classmethod
    def validate_currency(cls, v):
        """Validar código de moneda"""
        return v.upper()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "driver": {
                        "first_name": "Juan",
                        "last_name": "Pérez",
                        "email": "juan@example.com",
                        "phone": "+52 999 123 4567"
                    },
                    "supplier_id": 1,
                    "vehicle_id": 42,
                    "acriss_code": "ECAR",
                    "pickup_office_id": 10,
                    "pickup_datetime": "2025-02-01T10:00:00",
                    "dropoff_office_id": 10,
                    "dropoff_datetime": "2025-02-05T10:00:00",
                    "price": 1500.00,
                    "currency_code": "USD",
                    "payment_method_id": "pm_1234567890"
                }
            ]
        }
    }


class ReservationResponse(BaseModel):
    """Schema para response de reserva"""

    reservation_id: int
    reservation_code: str
    supplier_reservation_code: str | None
    status: str
    payment_status: str
    total_amount: Decimal
    currency_code: str
    receipt_url: str | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "reservation_id": 123,
                    "reservation_code": "RES-20250108-A3K9M",
                    "supplier_reservation_code": "LOC-789456",
                    "status": "CONFIRMED",
                    "payment_status": "PAID",
                    "total_amount": 1500.00,
                    "currency_code": "USD",
                    "receipt_url": "/receipts/receipt_RES-20250108-A3K9M.pdf",
                    "created_at": "2025-01-08T15:30:00"
                }
            ]
        }
    }


class ReservationDetailResponse(BaseModel):
    """Schema detallado de reserva"""

    reservation_id: int
    reservation_code: str
    supplier_reservation_code: str | None
    status: str
    payment_status: str

    # Dates
    pickup_datetime: datetime
    dropoff_datetime: datetime
    rental_days: int

    # Pricing
    total_amount: Decimal
    currency_code: str

    # Supplier
    supplier_name: str | None

    # Offices
    pickup_office_name: str | None
    dropoff_office_name: str | None

    # Vehicle
    car_category_name: str | None
    acriss_code: str | None

    # Driver
    driver_name: str | None = None
    driver_email: str | None = None

    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema para errores"""

    error: str
    message: str
    code: str | None = None
    details: dict | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "PaymentFailed",
                    "message": "Payment processing failed",
                    "code": "PAYMENT_FAILED",
                    "details": {"reason": "insufficient_funds"}
                }
            ]
        }
    }
