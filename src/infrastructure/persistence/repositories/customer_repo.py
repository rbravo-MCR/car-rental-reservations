"""
Customer Repository Implementation (CON ORM)
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import AppCustomerModel


class SQLAlchemyCustomerRepository:
    """Implementación de CustomerRepository con ORM"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, customer_id: int) -> dict[str, Any] | None:
        """Obtener cliente por ID"""
        stmt = select(AppCustomerModel).where(
            AppCustomerModel.id == customer_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            'id': model.id,
            'email': model.email,
            'first_name': model.first_name,
            'last_name': model.last_name,
            'phone': model.phone,
            'country_id': model.country_id,
            'status': model.status,
        }

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Obtener cliente por email"""
        stmt = select(AppCustomerModel).where(AppCustomerModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            'id': model.id,
            'email': model.email,
            'first_name': model.first_name,
            'last_name': model.last_name,
            'phone': model.phone,
            'status': model.status,
        }
