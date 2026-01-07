"""
Receipt Generator Interface
Genera recibos en PDF
"""
from typing import Protocol

from domain.entities.payment import Payment

from domain.entities.reservation import Reservation


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
