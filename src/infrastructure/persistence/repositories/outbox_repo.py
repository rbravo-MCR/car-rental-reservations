"""
Outbox Repository Implementation
"""
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.persistence.models import OutboxEventModel


class SQLAlchemyOutboxRepository:
    """Implementación de OutboxRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: int,
        payload: dict[str, Any]
    ) -> int:
        """Crear evento en outbox"""
        model = OutboxEventModel(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            status='NEW',
            attempts=0,
        )

        self.session.add(model)
        await self.session.flush()

        return model.id

    async def get_pending_events(self, batch_size: int = 10) -> list[dict[str, Any]]:
        """Obtener eventos pendientes de procesar"""
        now = datetime.utcnow()

        stmt = (
            select(OutboxEventModel)
            .where(
                and_(
                    OutboxEventModel.status == 'NEW',
                    or_(
                        OutboxEventModel.next_attempt_at.is_(None),
                        OutboxEventModel.next_attempt_at <= now
                    )
                )
            )
            .order_by(OutboxEventModel.created_at.asc())
            .limit(batch_size)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        events = []
        for model in models:
            events.append({
                'id': model.id,
                'event_type': model.event_type,
                'aggregate_type': model.aggregate_type,
                'aggregate_id': model.aggregate_id,
                'payload': model.payload,
                'attempts': model.attempts,
            })

        return events

    async def mark_as_processed(self, event_id: int) -> None:
        """Marcar evento como procesado"""
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.status = 'DONE'
        model.updated_at = datetime.utcnow()

        await self.session.flush()

    async def mark_as_failed(self, event_id: int, error_message: str) -> None:
        """Marcar evento como fallido y programar reintento"""
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.attempts += 1

        # Backoff exponencial: 1min, 2min, 4min, 8min, 16min
        delay_minutes = 2 ** model.attempts
        model.next_attempt_at = datetime.utcnow() + timedelta(minutes=delay_minutes)

        # Si supera max intentos, marcar como FAILED
        if model.attempts >= 5:
            model.status = 'FAILED'

        model.updated_at = datetime.utcnow()

        await self.session.flush()
