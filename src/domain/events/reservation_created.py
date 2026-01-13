"""
Domain Event: Reservation Created
"""
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ReservationCreated:
    """
    Evento que se dispara cuando una reserva es creada.
    """
    aggregate_id: int | None
    reservation_code: str
    pickup_datetime: datetime
    total_amount: str
    currency_code: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)