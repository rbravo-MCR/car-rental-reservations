"""
Payment Gateway Interface
Define contrato para procesadores de pago
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol


@dataclass
class PaymentResult:
    """Resultado de un pago"""
    success: bool
    payment_intent_id: str
    charge_id: str | None = None
    amount: Decimal = Decimal("0.00")
    currency_code: str = "USD"
    status: str = "pending"
    method: str | None = None
    error_message: str | None = None


class PaymentGateway(Protocol):
    """Interface para gateway de pagos (Stripe)"""

    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_method_id: str,
        description: str,
        metadata: dict[str, str] | None = None,
    ) -> PaymentResult:
        """
        Procesar cargo inmediato
        Args:
            amount: Monto a cobrar
            currency: Código de moneda (ISO 4217)
            payment_method_id: ID del método de pago de Stripe
            description: Descripción del cargo
            metadata: Metadata adicional
        Returns:
            PaymentResult con detalles del cargo
        """
        ...

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> dict[str, Any]:
        """
        Verificar firma de webhook de Stripe
        Returns:
            Evento parseado si la firma es válida
        """
        ...


class IdempotencyStore(Protocol):
    """Interface para almacenar claves de idempotencia"""

    async def get(
        self,
        scope: str,
        key: str
    ) -> dict[str, Any] | None:
        """Obtener resultado cacheado"""
        ...

    async def set(
        self,
        scope: str,
        key: str,
        request_hash: str,
        response: dict[str, Any],
        http_status: int,
        reference_id: int | None = None,
    ) -> None:
        """Guardar resultado"""
        ...
