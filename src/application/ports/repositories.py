"""
Repository Interfaces (Ports)
Define contratos que la infraestructura debe implementar
"""
from datetime import datetime
from typing import Any, Protocol

from src.domain.entities.payment import Payment

from src.domain.entities.reservation import Reservation


class ReservationRepository(Protocol):
    """Interface para repositorio de reservas"""

    async def get_by_id(self, reservation_id: int) -> Reservation | None:
        """Obtener reserva por ID"""
        ...

    async def get_by_code(self, reservation_code: str) -> Reservation | None:
        """Obtener reserva por código"""
        ...

    async def exists_by_code(self, reservation_code: str) -> bool:
        """Verificar si existe código de reserva"""
        ...

    async def save(self, reservation: Reservation) -> Reservation:
        """Guardar reserva (insert o update)"""
        ...

    async def update(self, reservation: Reservation) -> Reservation:
        """Actualizar reserva existente"""
        ...

    async def list_by_customer(
        self,
        customer_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Reservation]:
        """Listar reservas de un cliente"""
        ...

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        supplier_id: int | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Reservation]:
        """Listar reservas en un rango de fechas"""
        ...

    async def check_availability(
        self,
        car_category_id: int,
        supplier_id: int,
        pickup_datetime: datetime,
        dropoff_datetime: datetime
    ) -> bool:
        """Verificar disponibilidad (no hay overlaps)"""
        ...


class PaymentRepository(Protocol):
    """Interface para repositorio de pagos"""

    async def get_by_id(self, payment_id: int) -> Payment | None:
        """Obtener pago por ID"""
        ...

    async def get_by_reservation_id(self, reservation_id: int) -> list[Payment]:
        """Obtener pagos de una reserva"""
        ...

    async def get_by_stripe_payment_intent(
        self,
        payment_intent_id: str
    ) -> Payment | None:
        """Obtener pago por Payment Intent de Stripe"""
        ...

    async def save(self, payment: Payment) -> Payment:
        """Guardar pago"""
        ...

    async def update(self, payment: Payment) -> Payment:
        """Actualizar pago"""
        ...


class SupplierRequestRepository(Protocol):
    """Interface para audit log de requests a suppliers"""

    async def create(
        self,
        reservation_id: int,
        supplier_id: int,
        request_type: str,
        status: str,
        idem_key: str | None = None,
        attempt: int = 0,
        http_status: int | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        request_payload: dict[str, Any] | None = None,
        response_payload: dict[str, Any] | None = None,
    ) -> int:
        """Registrar request al supplier"""
        ...


class OutboxRepository(Protocol):
    """Interface para outbox events"""

    async def create(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: int,
        payload: dict[str, Any]
    ) -> int:
        """Crear evento en outbox"""
        ...

    async def get_pending_events(
        self,
        batch_size: int = 10
    ) -> list[dict[str, Any]]:
        """Obtener eventos pendientes de procesar"""
        ...

    async def mark_as_processed(self, event_id: int) -> None:
        """Marcar evento como procesado"""
        ...

    async def mark_as_failed(
        self,
        event_id: int,
        error_message: str
    ) -> None:
        """Marcar evento como fallido"""
        ...


class CustomerRepository(Protocol):
    """Interface para repositorio de clientes"""

    async def get_by_id(self, customer_id: int) -> dict[str, Any] | None:
        """Obtener cliente por ID"""
        ...

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Obtener cliente por email"""
        ...


class SupplierRepository(Protocol):
    """Interface para repositorio de suppliers"""

    async def get_by_id(self, supplier_id: int) -> dict[str, Any] | None:
        """Obtener supplier por ID"""
        ...

    async def get_active_suppliers(self) -> list[dict[str, Any]]:
        """Obtener suppliers activos"""
        ...


class OfficeRepository(Protocol):
    """Interface para repositorio de oficinas"""

    async def get_by_id(self, office_id: int) -> dict[str, Any] | None:
        """Obtener oficina por ID"""
        ...

    async def get_by_supplier(
        self,
        supplier_id: int,
        is_active: bool = True
    ) -> list[dict[str, Any]]:
        """Obtener oficinas de un supplier"""
        ...
