"""
Pricing Item Entity
Item de precio de una reserva (base rate, tax, fee, etc)
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PricingItemType(str, Enum):
    """Tipos de items de precio"""
    BASE_RATE = "BASE_RATE"
    TAX = "TAX"
    FEE = "FEE"
    EXTRA = "EXTRA"
    INSURANCE = "INSURANCE"
    DISCOUNT = "DISCOUNT"
    OTHER = "OTHER"


@dataclass
class PricingItem:
    """Entity: Item de precio"""

    id: int | None = None
    reservation_id: int | None = None
    item_type: PricingItemType = PricingItemType.BASE_RATE
    description: str = ""
    quantity: Decimal = Decimal("1.00")
    unit_price_public: Decimal = Decimal("0.00")
    unit_price_supplier: Decimal = Decimal("0.00")
    total_price_public: Decimal = Decimal("0.00")
    total_price_supplier: Decimal = Decimal("0.00")

    def __post_init__(self):
        """Convertir a Decimal si es necesario"""
        for field_name in ['quantity', 'unit_price_public', 'unit_price_supplier',
                           'total_price_public', 'total_price_supplier']:
            value = getattr(self, field_name)
            if not isinstance(value, Decimal):
                setattr(self, field_name, Decimal(str(value)))

    def calculate_totals(self) -> None:
        """Calcular totales basados en cantidad y precio unitario"""
        self.total_price_public = self.quantity * self.unit_price_public
        self.total_price_supplier = self.quantity * self.unit_price_supplier
