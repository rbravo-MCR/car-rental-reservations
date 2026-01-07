"""
List Reservations Use Case
Listar reservas con filtros
"""
import structlog

from application.dto.reservation_dto import ListReservationsDTO
from application.ports.unit_of_work import UnitOfWork
from domain.entities.reservation import Reservation

logger = structlog.get_logger()


class ListReservationsUseCase:
    """
    Use Case: Listar reservas con filtros
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, dto: ListReservationsDTO) -> list[Reservation]:
        """Ejecutar caso de uso"""

        async with self.uow:
            # Listar por cliente
            if dto.customer_id:
                reservations = await self.uow.reservations.list_by_customer(
                    customer_id=dto.customer_id,
                    limit=dto.limit,
                    offset=dto.offset,
                )
                logger.info(
                    "reservations_listed_by_customer",
                    customer_id=dto.customer_id,
                    count=len(reservations),
                )

            # Listar por rango de fechas
            elif dto.start_date and dto.end_date:
                reservations = await self.uow.reservations.list_by_date_range(
                    start_date=dto.start_date,
                    end_date=dto.end_date,
                    limit=dto.limit,
                    offset=dto.offset,
                )
                logger.info(
                    "reservations_listed_by_date_range",
                    start=dto.start_date.isoformat(),
                    end=dto.end_date.isoformat(),
                    count=len(reservations),
                )

            else:
                # Sin filtros, retornar vacío o error
                logger.warning("list_reservations_without_filters")
                return []

            return reservations
