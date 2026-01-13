"""
Payment Entity
Pago de una reserva
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.domain.value_objects.reservation_status import PaymentStatus


@dataclass
class Payment:
    """Entity: Pago"""

    id: int | None = None
    reservation_id: int | None = None
    provider: str = "STRIPE"
    provider_transaction_id: str | None = None
    method: str | None = None
    amount: Decimal = Decimal("0.00")
    currency_code: str = "USD"
    status: PaymentStatus = PaymentStatus.UNPAID
    captured_at: datetime | None = None
    refunded_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # Stripe specific
    stripe_payment_intent_id: str | None = None
    stripe_charge_id: str | None = None
    stripe_event_id: str | None = None
    amount_refunded: Decimal = Decimal("0.00")
    fee_amount: Decimal | None = None
    net_amount: Decimal | None = None

    def __post_init__(self) -> None:
        """Validaciones"""
        if self.amount < 0:
            raise ValueError("Payment amount cannot be negative")

        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

        if not isinstance(self.amount_refunded, Decimal):
            self.amount_refunded = Decimal(str(self.amount_refunded))

    @classmethod
    def create(
        cls,
        reservation_id: int,
        provider: str,
        provider_transaction_id: str,
        amount: Decimal,
        currency_code: str,
        status: PaymentStatus,
        method: str | None = None,
        stripe_payment_intent_id: str | None = None,
    ) -> Payment:
        """Factory method para crear pago"""
        return cls(
            reservation_id=reservation_id,
            provider=provider,
            provider_transaction_id=provider_transaction_id,
            amount=amount,
            currency_code=currency_code,
            status=status,
            method=method,
            stripe_payment_intent_id=stripe_payment_intent_id,
        )

    def mark_as_captured(self, charge_id: str) -> None:
        """Marcar pago como capturado"""
        self.status = PaymentStatus.PAID
        self.captured_at = datetime.utcnow()
        self.stripe_charge_id = charge_id

    def is_successful(self) -> bool:
        """Verifica si el pago fue exitoso"""
        return self.status == PaymentStatus.PAID
