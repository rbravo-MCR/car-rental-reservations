"""
Reservation Code Generator
Genera códigos únicos de reserva
"""
import random
import string
from datetime import datetime


class ReservationCodeGenerator:
    """
    Genera códigos únicos de reserva
    Formato: RES-YYYYMMDD-XXXXX
    Ejemplo: RES-20250108-A3K9M
    """

    PREFIX = "RES"
    RANDOM_LENGTH = 5

    @staticmethod
    def generate() -> str:
        """
        Genera un código de reserva

        Returns:
            str: Código en formato RES-YYYYMMDD-XXXXX
        """
        date_part = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=ReservationCodeGenerator.RANDOM_LENGTH
            )
        )
        return f"{ReservationCodeGenerator.PREFIX}-{date_part}-{random_part}"

    @staticmethod
    async def generate_unique(repository) -> str:
        """
        Genera código único verificando que no existe en DB

        Args:
            repository: Repository con método exists_by_code

        Returns:
            str: Código único

        Raises:
            RuntimeError: Si no puede generar código único después de 10 intentos
        """
        max_attempts = 10

        for attempt in range(max_attempts):
            code = ReservationCodeGenerator.generate()
            exists = await repository.exists_by_code(code)

            if not exists:
                return code

        # Si llegamos aquí, algo está muy mal
        raise RuntimeError(
            f"Failed to generate unique reservation code after {max_attempts} attempts"
        )

    @staticmethod
    def validate_format(code: str) -> bool:
        """
        Valida formato de código de reserva

        Args:
            code: Código a validar

        Returns:
            bool: True si el formato es válido
        """
        if not code:
            return False

        parts = code.split('-')

        # Debe tener 3 partes
        if len(parts) != 3:
            return False

        prefix, date_part, random_part = parts

        # Validar prefix
        if prefix != ReservationCodeGenerator.PREFIX:
            return False

        # Validar date part (8 dígitos)
        if len(date_part) != 8 or not date_part.isdigit():
            return False

        # Validar random part (5 caracteres alfanuméricos)
        if len(random_part) != ReservationCodeGenerator.RANDOM_LENGTH:
            return False

        if not random_part.isalnum():
            return False

        return True
