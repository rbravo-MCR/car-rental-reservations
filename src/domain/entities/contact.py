"""
Contact Entity
Contacto de una reserva (booker, emergency)
"""
from dataclasses import dataclass
from enum import Enum


class ContactType(str, Enum):
    """Tipos de contacto"""
    BOOKER = "BOOKER"            # Quien hizo la reserva
    EMERGENCY = "EMERGENCY"      # Contacto de emergencia


@dataclass
class Contact:
    """Entity: Contacto"""

    id: int | None = None
    reservation_id: int | None = None
    contact_type: ContactType = ContactType.BOOKER
    full_name: str = ""
    email: str = ""
    phone: str | None = None

    def __post_init__(self) -> None:
        """Validaciones"""
        if not self.full_name:
            raise ValueError("Contact must have a name")
        if not self.email:
            raise ValueError("Contact must have an email")
