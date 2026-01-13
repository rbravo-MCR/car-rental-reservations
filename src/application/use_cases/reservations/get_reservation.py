"""
Get Reservation Use Case
Consultar una reserva por ID o código
"""
import structlog

from src.application.dto.reservation_dto import GetReservationDTO
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.reservation import Reservation
from src.domain.exceptions.reservation_errors import ReservationNotFoundError

logger = structlog.get_logger()


class GetReservationUseCase:
    """
    Use Case: Obtener reserva por ID o código
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, dto: GetReservationDTO) -> Reservation:
        """Ejecutar caso de uso"""

        async with self.uow:
            # Buscar por ID o código
            if dto.reservation_id:
                reservation = await self.uow.reservations.get_by_id(
                    dto.reservation_id
                )
                identifier = f"ID {dto.reservation_id}"
            elif dto.reservation_code:
                reservation = await self.uow.reservations.get_by_code(
                    dto.reservation_code
                )
                identifier = f"code {dto.reservation_code}"
            else:
                raise ValueError(
                    "Must provide reservation_id or reservation_code")

            if not reservation:
                logger.warning("reservation_not_found", identifier=identifier)
                raise ReservationNotFoundError(identifier)

            logger.info(
                "reservation_retrieved",
                reservation_id=reservation.id,
                code=reservation.reservation_code,
            )

            return reservation
