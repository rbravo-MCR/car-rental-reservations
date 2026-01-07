"""
Supplier Gateway Interface
Define contrato para integraciones con proveedores
"""
from datetime import datetime
from typing import Any, Protocol


class SupplierGateway(Protocol):
    """
    Interface para gateway de suppliers
    Todas las implementaciones específicas deben seguir este contrato
    """

    supplier_id: int
    supplier_name: str

    async def search_availability(
        self,
        pickup_office_code: str,
        dropoff_office_code: str,
        pickup_datetime: datetime,
        dropoff_datetime: datetime,
        driver_age: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Buscar disponibilidad de vehículos
        Returns:
            Lista de vehículos disponibles con estructura:
            {
                'vehicle_code': str,
                'acriss_code': str,
                'vehicle_name': str,
                'total_price': Decimal,
                'currency_code': str,
                'supplier_product_code': str,
            }
        """
        ...

    async def create_reservation(
        self,
        reservation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Crear reserva en el sistema del supplier
        Args:
            reservation_data: Datos de la reserva con estructura:
            {
                'internal_code': str,
                'pickup_office_code': str,
                'dropoff_office_code': str,
                'pickup_datetime': datetime,
                'dropoff_datetime': datetime,
                'vehicle_code': str,
                'driver': {
                    'first_name': str,
                    'last_name': str,
                    'email': str,
                    'phone': str,
                }
            }
        Returns:
            Resultado con estructura:
            {
                'confirmation_number': str,
                'status': str,
                'total_price': Decimal,
                'currency_code': str,
            }
        """
        ...

    async def confirm_reservation(
        self,
        supplier_reservation_code: str
    ) -> dict[str, Any]:
        """
        Confirmar reserva (solo si el supplier usa flujo de 2 pasos)

        Returns:
            {
                'confirmation_number': str,
                'status': str,
            }
        """
        ...

    async def get_reservation_status(
        self,
        supplier_reservation_code: str
    ) -> dict[str, Any]:
        """
        Consultar estado de reserva

        Returns:
            {
                'confirmation_number': str,
                'status': str,
                'pickup_completed': bool,
                'dropoff_completed': bool,
            }
        """
        ...

    async def close(self) -> None:
        """Cerrar conexiones HTTP"""
        ...
