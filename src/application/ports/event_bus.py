"""
Event Bus Interface
Para publicar eventos de dominio
"""
from typing import Any, Protocol


class EventBus(Protocol):
    """Interface para event bus"""

    async def publish(
        self,
        event_type: str,
        aggregate_id: int,
        payload: dict[str, Any]
    ) -> None:
        """Publicar evento"""
        ...

    async def publish_batch(
        self,
        events: list[dict[str, Any]]
    ) -> None:
        """Publicar múltiples eventos"""
        ...
