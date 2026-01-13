"""
Reservation Status Value Objects
Enums para estados de reserva y pago
"""
from enum import Enum


class ReservationStatus(str, Enum):
    """Estado de la reserva"""
    PENDING = "pending"
    ON_REQUEST = "on_request"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Estado del pago"""
    UNPAID = "unpaid"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
