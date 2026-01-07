"""
Office Repository Implementation
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.persistence.models import CityModel, OfficeModel


class SQLAlchemyOfficeRepository:
    """Implementación de OfficeRepository con ORM"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, office_id: int) -> dict[str, Any] | None:
        """Obtener oficina por ID"""
        stmt = (
            select(OfficeModel)
            .where(OfficeModel.id == office_id)
            .options(selectinload(OfficeModel.city).selectinload(CityModel.country))
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            'id': model.id,
            'supplier_id': model.supplier_id,
            'city_id': model.city_id,
            'code': model.code,
            'name': model.name,
            'type': model.type,
            'iata_code': model.iata_code,
            'address_line1': model.address_line1,
            'latitude': float(model.latitude) if model.latitude else None,
            'longitude': float(model.longitude) if model.longitude else None,
            'is_active': model.is_active,
            'city_name': model.city.name if model.city else None,
            'country_name': model.city.country.name if model.city and model.city.country else None,
            'country_code': model.city.country.iso_code if model.city and model.city.country else None,
        }

    async def get_by_supplier(
        self,
        supplier_id: int,
        is_active: bool = True
    ) -> list[dict[str, Any]]:
        """Obtener oficinas de un supplier"""
        stmt = (
            select(OfficeModel)
            .where(
                OfficeModel.supplier_id == supplier_id,
                OfficeModel.is_active == is_active
            )
            .options(selectinload(OfficeModel.city))
            .order_by(OfficeModel.name)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        offices = []
        for model in models:
            offices.append({
                'id': model.id,
                'code': model.code,
                'name': model.name,
                'type': model.type,
                'iata_code': model.iata_code,
                'is_active': model.is_active,
                'city_name': model.city.name if model.city else None,
            })

        return offices
