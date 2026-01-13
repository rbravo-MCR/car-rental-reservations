"""
Unit of Work Implementation
Coordina múltiples repositorios en una transacción
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import (
    CustomerRepository,
    OfficeRepository,
    OutboxRepository,
    PaymentRepository,
    ReservationRepository,
    SupplierRepository,
    SupplierRequestRepository,
)
from src.infrastructure.persistence.database import async_session_factory
from src.infrastructure.persistence.repositories.customer_repo import SQLAlchemyCustomerRepository
from src.infrastructure.persistence.repositories.office_repo import SQLAlchemyOfficeRepository
from src.infrastructure.persistence.repositories.outbox_repo import SQLAlchemyOutboxRepository
from src.infrastructure.persistence.repositories.payment_repo import SQLAlchemyPaymentRepository
from src.infrastructure.persistence.repositories.reservation_repo import (
    SQLAlchemyReservationRepository,
)
from src.infrastructure.persistence.repositories.supplier_repo import SQLAlchemySupplierRepository
from src.infrastructure.persistence.repositories.supplier_request_repo import (
    SQLAlchemySupplierRequestRepository,
)


class SQLAlchemyUnitOfWork:
    """
    Implementación de Unit of Work con SQLAlchemy
    Maneja transacciones y coordina repositorios
    """

    def __init__(self) -> None:
        self.session: AsyncSession | None = None
        self._reservations = None
        self._payments = None
        self._supplier_requests = None
        self._outbox = None
        self._customers = None
        self._suppliers = None
        self._offices = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        """Iniciar transacción"""
        self.session = async_session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Finalizar transacción"""
        if exc_type is not None:
            # Si hubo excepción, rollback
            await self.rollback()

        if self.session:
            await self.session.close()

    async def commit(self) -> None:
        """Confirmar transacción"""
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        """Revertir transacción"""
        if self.session:
            await self.session.rollback()

    @property
    def reservations(self) -> ReservationRepository:
        """Repository de reservas (lazy loading)"""
        if self._reservations is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._reservations = SQLAlchemyReservationRepository(self.session)
        return self._reservations

    @property
    def payments(self) -> PaymentRepository:
        """Repository de pagos"""
        if self._payments is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._payments = SQLAlchemyPaymentRepository(self.session)
        return self._payments

    @property
    def supplier_requests(self) -> SupplierRequestRepository:
        """Repository de supplier requests"""
        if self._supplier_requests is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._supplier_requests = SQLAlchemySupplierRequestRepository(
                self.session)
        return self._supplier_requests

    @property
    def outbox(self) -> OutboxRepository:
        """Repository de outbox"""
        if self._outbox is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._outbox = SQLAlchemyOutboxRepository(self.session)
        return self._outbox

    @property
    def customers(self) -> CustomerRepository:
        """Repository de customers"""
        if self._customers is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._customers = SQLAlchemyCustomerRepository(self.session)
        return self._customers

    @property
    def suppliers(self) -> SupplierRepository:
        """Repository de suppliers"""
        if self._suppliers is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._suppliers = SQLAlchemySupplierRepository(self.session)
        return self._suppliers

    @property
    def offices(self) -> OfficeRepository:
        """Repository de offices"""
        if self._offices is None:
            if self.session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._offices = SQLAlchemyOfficeRepository(self.session)
        return self._offices


async def get_uow() -> AsyncGenerator[SQLAlchemyUnitOfWork]:
    """
    Dependency para FastAPI
    Uso:
        @app.post("/endpoint")
        async def endpoint(uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
            async with uow:
                # usar uow.reservations, etc
                await uow.commit()
    """
    uow = SQLAlchemyUnitOfWork()
    try:
        yield uow
    finally:
        pass

# ✅ PERSISTENCE LAYER COMPLETADO
"""
Has creado ** 8 archivos de persistencia ** (38-45):
- ✅ ReservationRepository(completo)
- ✅ PaymentRepository
- ✅ OutboxRepository
- ✅ SupplierRequestRepository
- ✅ CustomerRepository
- ✅ SupplierRepository
- ✅ OfficeRepository
- ✅ ** Unit of Work ** (coordina todos los repos)

"""

# 📊 PROGRESO TOTAL
"""
✅ Config:         5 archivos
✅ Domain:        21 archivos
✅ Application:   15 archivos
✅ Infrastructure:
   - Database:     2 archivos
   - Repositories: 8 archivos
───────────────────────────────
Total:           51 archivos
"""
