"""
Pydantic Schemas for Availability endpoints
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class AvailabilitySearchRequest(BaseModel):
    """Schema para búsqueda de disponibilidad"""

    pickup_office_id: int = Field(..., gt=0)
    dropoff_office_id: int = Field(..., gt=0)
    pickup_datetime: datetime
    dropoff_datetime: datetime
    driver_age: int | None = Field(None, ge=18, le=99)
    supplier_id: int | None = Field(None, gt=0)

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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pickup_office_id": 10,
                    "dropoff_office_id": 10,
                    "pickup_datetime": "2025-02-01T10:00:00",
                    "dropoff_datetime": "2025-02-05T10:00:00",
                    "driver_age": 30,
                    "supplier_id": 1
                }
            ]
        }
    }


class VehicleAvailabilityResponse(BaseModel):
    """Schema para vehículo disponible"""

    supplier_id: int
    supplier_name: str
    vehicle_id: int
    vehicle_name: str
    acriss_code: str
    car_category_name: str

    # Pricing
    total_price: Decimal
    daily_rate: Decimal
    currency_code: str

    # Details
    doors: int | None = None
    seats: int | None = None
    transmission: str | None = None
    air_conditioning: bool = True

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "supplier_id": 1,
                    "supplier_name": "LOCALIZA",
                    "vehicle_id": 42,
                    "vehicle_name": "Toyota Corolla or similar",
                    "acriss_code": "ICAR",
                    "car_category_name": "Intermediate",
                    "total_price": 1500.00,
                    "daily_rate": 375.00,
                    "currency_code": "USD",
                    "doors": 4,
                    "seats": 5,
                    "transmission": "Automatic",
                    "air_conditioning": True
                }
            ]
        }
    }
