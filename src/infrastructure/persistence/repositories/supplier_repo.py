"""
Supplier Repository Implementation
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import SupplierModel


class SQLAlchemySupplierRepository:
    """Implementación de SupplierRepository con ORM"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, supplier_id: int) -> dict[str, Any] | None:
        """Obtener supplier por ID"""
        stmt = select(SupplierModel).where(SupplierModel.id == supplier_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            'id': model.id,
            'name': model.name,
            'legal_name': model.legal_name,
            'website_url': model.website_url,
            'support_email': model.support_email,
            'support_phone': model.support_phone,
            'is_active': model.is_active,
            'brand_id': model.brand_id,
            'country_code': model.country_code,
        }

    async def get_active_suppliers(self) -> list[dict[str, Any]]:
        """Obtener suppliers activos"""
        stmt = (
            select(SupplierModel)
            .where(SupplierModel.is_active)
            .order_by(SupplierModel.name)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        suppliers = []
        for model in models:
            suppliers.append({
                'id': model.id,
                'name': model.name,
                'legal_name': model.legal_name,
                'country_code': model.country_code,
                'is_active': model.is_active,
            })

        return suppliers
