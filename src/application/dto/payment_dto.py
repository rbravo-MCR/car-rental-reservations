"""
Payment DTOs
Input/Output para operaciones de pago
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class ProcessPaymentDTO:
    """DTO para procesar pago"""

    reservation_id: int
    payment_method_id: str
    amount: Decimal
    currency_code: str
    description: str | None = None
    metadata: dict[str, str] | None = None


@dataclass
class PaymentResultDTO:
    """DTO para resultado de pago"""

    payment_id: int
    reservation_id: int
    provider: str
    provider_transaction_id: str
    stripe_payment_intent_id: str | None
    stripe_charge_id: str | None
    amount: Decimal
    currency_code: str
    status: str
    method: str | None
    created_at: datetime


@dataclass
class WebhookEventDTO:
    """DTO para evento de webhook"""

    event_id: str
    event_type: str
    provider: str
    payload: dict
    signature: str | None = None
