"""
Idempotency Store Implementation
Almacena claves de idempotencia para evitar duplicados
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.persistence.models import IdempotencyKeyModel

logger = structlog.get_logger()


class MySQLIdempotencyStore:
    """
    Implementación de IdempotencyStore con MySQL

    Uso:
    - Scope: categoría de operación ('reservations', 'payments', etc)
    - Key: identificador único del request (UUID, hash, etc)
    - Request hash: hash del payload para detectar requests duplicados con diferente payload
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        scope: str,
        key: str
    ) -> dict[str, Any] | None:
        """
        Obtener resultado cacheado por scope + key
        Args:
            scope: Categoría de operación
            key: Identificador único
        Returns:
            dict con response_json, http_status, reference_id si existe
            None si no existe
        """
        stmt = select(IdempotencyKeyModel).where(
            IdempotencyKeyModel.scope == scope,
            IdempotencyKeyModel.idem_key == key,
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            logger.debug("idempotency_key_not_found", scope=scope, key=key)
            return None

        logger.info(
            "idempotency_key_found",
            scope=scope,
            key=key,
            reference_id=model.reference_reservation_id,
        )

        return {
            'response_json': model.response_json,
            'http_status': model.http_status,
            'reference_id': model.reference_reservation_id,
            'request_hash': model.request_hash,
            'created_at': model.created_at,
        }

    async def set(
        self,
        scope: str,
        key: str,
        request_hash: str,
        response: dict[str, Any],
        http_status: int,
        reference_id: int | None = None,
    ) -> None:
        """
        Guardar resultado para idempotencia

        Args:
            scope: Categoría de operación
            key: Identificador único
            request_hash: Hash del request payload
            response: Response JSON a cachear
            http_status: Status code HTTP
            reference_id: ID de la reserva/pago creado (opcional)
        """
        # Verificar si ya existe
        existing = await self.get(scope, key)
        if existing:
            logger.warning(
                "idempotency_key_already_exists",
                scope=scope,
                key=key,
            )
            return

        model = IdempotencyKeyModel(
            scope=scope,
            idem_key=key,
            request_hash=request_hash,
            response_json=response,
            http_status=http_status,
            reference_reservation_id=reference_id,
        )

        self.session.add(model)
        await self.session.flush()

        logger.info(
            "idempotency_key_saved",
            scope=scope,
            key=key,
            reference_id=reference_id,
        )

    async def cleanup_old_keys(self, days: int = 7) -> int:
        """
        Limpiar claves antiguas (TTL cleanup)
        Args:
            days: Días de antigüedad para eliminar
        Returns:
            int: Número de claves eliminadas
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = delete(IdempotencyKeyModel).where(
            IdempotencyKeyModel.created_at < cutoff_date
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        deleted_count = result.rowcount

        logger.info(
            "idempotency_keys_cleaned",
            deleted_count=deleted_count,
            days=days,
        )

        return deleted_count


def compute_request_hash(payload: dict[str, Any]) -> str:
    """
    Calcular hash SHA256 del payload del request
    Útil para detectar requests duplicados con diferente payload

    Args:
        payload: Dict del request body
    Returns:
        str: Hash hexadecimal
    Example:
        >>> compute_request_hash({'driver': {'name': 'John'}})
        'a3f5d2e...'
    """
    # Serializar a JSON de forma determinística (sorted keys)
    json_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)

    # Calcular SHA256
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))

    return hash_obj.hexdigest()
