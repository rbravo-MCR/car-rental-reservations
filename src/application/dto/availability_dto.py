"""
Availability DTOs
Input/Output para búsqueda de disponibilidad
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class AvailabilitySearchDTO:
    """DTO para búsqueda de disponibilidad"""

    pickup_office_id: int
    dropoff_office_id: int
    pickup_datetime: datetime
    dropoff_datetime: datetime
    driver_age: int | None = None
    supplier_id: int | None = None  # Si se quiere filtrar por supplier


@dataclass
class AvailabilityResultDTO:
    """DTO para resultado de disponibilidad"""

    supplier_id: int
    supplier_name: str
    vehicle_id: int  # supplier_car_product_id
    vehicle_name: str
    acriss_code: str
    car_category_id: int
    car_category_name: str

    # Pricing
    total_price: Decimal
    daily_rate: Decimal
    currency_code: str

    # Vehicle details
    doors: int | None = None
    seats: int | None = None
    transmission: str | None = None
    air_conditioning: bool = True
    luggage_small: int | None = None
    luggage_large: int | None = None
    example_models: str | None = None

    # Availability
    available: bool = True
    supplier_product_code: str | None = None
