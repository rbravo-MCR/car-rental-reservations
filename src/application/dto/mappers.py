"""
Mappers entre Entities y DTOs
Convierte entre objetos de dominio y DTOs
"""
from src.application.dto.payment_dto import PaymentResultDTO
from src.application.dto.reservation_dto import ReservationResultDTO
from src.domain.entities.payment import Payment
from src.domain.entities.reservation import Reservation


class ReservationMapper:
    """Mapper para Reservation entity"""

    @staticmethod
    def to_result_dto(reservation: Reservation) -> ReservationResultDTO:
        """Convertir Reservation entity a DTO"""
        return ReservationResultDTO(
            reservation_id=reservation.id or 0,
            reservation_code=reservation.reservation_code,
            supplier_reservation_code=reservation.supplier_reservation_code,
            status=reservation.status.value,
            payment_status=reservation.payment_status.value,
            total_amount=reservation.public_price_total,
            currency_code=reservation.currency_code,
            receipt_url=None,
            created_at=reservation.created_at,
        )


class PaymentMapper:
    """Mapper para Payment entity"""

    @staticmethod
    def to_result_dto(payment: Payment) -> PaymentResultDTO:
        """Convertir Payment entity a DTO"""
        return PaymentResultDTO(
            payment_id=payment.id or 0,
            reservation_id=payment.reservation_id or 0,
            provider=payment.provider,
            provider_transaction_id=payment.provider_transaction_id or "",
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
            stripe_charge_id=payment.stripe_charge_id,
            amount=payment.amount,
            currency_code=payment.currency_code,
            status=payment.status.value,
            method=payment.method,
            created_at=payment.created_at,
        )
