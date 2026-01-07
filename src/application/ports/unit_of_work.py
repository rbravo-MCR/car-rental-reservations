"""
Unit of Work Interface
Patrón para manejar transacciones y coordinar repositorios
"""
from typing import Protocol

from application.ports.repositories import (
    CustomerRepository,
    OfficeRepository,
    OutboxRepository,
    PaymentRepository,
    ReservationRepository,
    SupplierRepository,
    SupplierRequestRepository,
)


class UnitOfWork(Protocol):
    """
    Interface para Unit of Work
    Coordina múltiples repositorios en una transacción
    """

    # Repositories
    reservations: ReservationRepository
    payments: PaymentRepository
    supplier_requests: SupplierRequestRepository
    outbox: OutboxRepository
    customers: CustomerRepository
    suppliers: SupplierRepository
    offices: OfficeRepository

    async def __aenter__(self) -> "UnitOfWork":
        """Iniciar contexto (transacción)"""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finalizar contexto"""
        ...

    async def commit(self) -> None:
        """Confirmar transacción"""
        ...

    async def rollback(self) -> None:
        """Revertir transacción"""
        ...
