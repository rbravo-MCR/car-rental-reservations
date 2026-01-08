"""
Supplier Request Repository Implementation
Audit log de requests a suppliers
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import SupplierRequestModel


class SQLAlchemySupplierRequestRepository:
    """Implementación de SupplierRequestRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

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
        model = SupplierRequestModel(
            reservation_id=reservation_id,
            supplier_id=supplier_id,
            request_type=request_type,
            idem_key=idem_key,
            attempt=attempt,
            status=status,
            http_status=http_status,
            error_code=error_code,
            error_message=error_message,
            request_payload=request_payload,
            response_payload=response_payload,
        )

        self.session.add(model)
        await self.session.flush()

        return model.id
