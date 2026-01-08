"""
Payment Repository Implementation
"""
from src.domain.entities.payment import Payment
from src.domain.value_objects.reservation_status import PaymentStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import PaymentModel


class SQLAlchemyPaymentRepository:
    """Implementación de PaymentRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, payment_id: int) -> Payment | None:
        """Obtener pago por ID"""
        stmt = select(PaymentModel).where(PaymentModel.id == payment_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_by_reservation_id(self, reservation_id: int) -> list[Payment]:
        """Obtener pagos de una reserva"""
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.reservation_id == reservation_id)
            .order_by(PaymentModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_stripe_payment_intent(
        self,
        payment_intent_id: str
    ) -> Payment | None:
        """Obtener pago por Payment Intent de Stripe"""
        stmt = select(PaymentModel).where(
            PaymentModel.stripe_payment_intent_id == payment_intent_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def save(self, payment: Payment) -> Payment:
        """Guardar pago nuevo"""
        model = PaymentModel(
            reservation_id=payment.reservation_id,
            provider=payment.provider,
            provider_transaction_id=payment.provider_transaction_id,
            method=payment.method,
            amount=payment.amount,
            currency_code=payment.currency_code,
            status=payment.status.value,
            captured_at=payment.captured_at,
            refunded_at=payment.refunded_at,
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
            stripe_charge_id=payment.stripe_charge_id,
            stripe_event_id=payment.stripe_event_id,
            amount_refunded=payment.amount_refunded,
            fee_amount=payment.fee_amount,
            net_amount=payment.net_amount,
        )

        self.session.add(model)
        await self.session.flush()

        payment.id = model.id
        return payment

    async def update(self, payment: Payment) -> Payment:
        """Actualizar pago"""
        stmt = select(PaymentModel).where(PaymentModel.id == payment.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.status = payment.status.value
        model.captured_at = payment.captured_at
        model.refunded_at = payment.refunded_at
        model.stripe_charge_id = payment.stripe_charge_id
        model.amount_refunded = payment.amount_refunded

        await self.session.flush()
        return payment

    def _to_entity(self, model: PaymentModel) -> Payment:
        """Convertir ORM model a entity"""
        return Payment(
            id=model.id,
            reservation_id=model.reservation_id,
            provider=model.provider,
            provider_transaction_id=model.provider_transaction_id,
            method=model.method,
            amount=model.amount,
            currency_code=model.currency_code,
            status=PaymentStatus(model.status),
            captured_at=model.captured_at,
            refunded_at=model.refunded_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            stripe_payment_intent_id=model.stripe_payment_intent_id,
            stripe_charge_id=model.stripe_charge_id,
            stripe_event_id=model.stripe_event_id,
            amount_refunded=model.amount_refunded,
            fee_amount=model.fee_amount,
            net_amount=model.net_amount,
        )
