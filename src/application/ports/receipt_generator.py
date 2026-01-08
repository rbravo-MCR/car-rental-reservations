"""
Receipt Generator Interface
Genera recibos en PDF
"""
from typing import Protocol

from src.domain.entities.payment import Payment

from src.domain.entities.reservation import Reservation


class ReceiptGenerator(Protocol):
    """Interface para generar recibos"""

    async def generate(
        self,
        reservation: Reservation,
        payment: Payment,
        supplier_confirmation: str,
    ) -> str:
        """
        Generar recibo en PDF
        Args:
            reservation: Reserva
            payment: Pago
            supplier_confirmation: Código de confirmación del supplier
        Returns:
            str: URL del PDF generado
        """
        ...
