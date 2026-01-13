"""
Domain Event: Reservation Confirmed
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReservationConfirmed:
    """
    Evento que se dispara cuando una reserva es confirmada.
    """
    aggregate_id: int | None
    reservation_code: str
    supplier_reservation_code: str
    supplier_name: str
    customer_email: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
