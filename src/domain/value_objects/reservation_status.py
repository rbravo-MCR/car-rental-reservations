"""
Reservation Status Value Objects
Enums para estados de reserva y pago
"""
from enum import Enum


class ReservationStatus(str, Enum):
    """Estado de la reserva"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Estado del pago"""
    UNPAID = "unpaid"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
