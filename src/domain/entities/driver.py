"""
Driver Entity
Conductor de una reserva
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class Driver:
    """Entity: Conductor"""

    id: int | None = None
    reservation_id: int | None = None
    app_customer_id: int | None = None
    is_primary_driver: bool = True
    first_name: str = ""
    last_name: str = ""
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    driver_license_number: str | None = None
    driver_license_country: str | None = None

    def __post_init__(self) -> None:
        """Validaciones básicas"""
        if not self.first_name or not self.last_name:
            raise ValueError("Driver must have first and last name")

    @property
    def full_name(self) -> str:
        """Nombre completo"""
        return f"{self.first_name} {self.last_name}"

    def is_valid_for_rental(self) -> bool:
        """Verifica si el conductor es válido para rentar"""
        # Debe tener licencia
        if not self.driver_license_number:
            return False

        # Debe tener al menos 21 años (si tenemos fecha de nacimiento)
        if self.date_of_birth:
            from datetime import datetime
            age = (datetime.now().year - self.date_of_birth.year)
            if age < 21:
                return False

        return True
