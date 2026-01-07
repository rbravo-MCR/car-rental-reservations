"""
Base Supplier Client
Clase abstracta con lógica común para todos los suppliers
"""
from abc import ABC, abstractmethod
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


class BaseSupplierClient(ABC):
    """
    Clase base abstracta para clientes de suppliers
    Proporciona lógica común (HTTP, retry, logging)
    """

    def __init__(
        self,
        supplier_id: int,
        supplier_name: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        self.logger = logger.bind(supplier=supplier_name)

    async def _get_client(self) -> httpx.AsyncClient:
        """Cliente HTTP reutilizable"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=10),
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Wrapper para requests con retry, logging, y error handling
        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: Endpoint relativo
            **kwargs: Argumentos adicionales (json, headers, etc)
        Returns:
            httpx.Response
        Raises:
            httpx.HTTPStatusError: Si status code es error
            httpx.RequestError: Si hay error de red
        """
        client = await self._get_client()

        for attempt in range(self.max_retries):
            try:
                self.logger.info(
                    "supplier_request",
                    method=method,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                )

                response = await client.request(method, endpoint, **kwargs)
                response.raise_for_status()

                self.logger.info(
                    "supplier_response_success",
                    status_code=response.status_code,
                    endpoint=endpoint,
                )

                return response

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    "supplier_http_error",
                    status_code=e.response.status_code,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                    error=str(e),
                )

                # Si es 4xx, no reintentar (error del cliente)
                if 400 <= e.response.status_code < 500:
                    raise

                # Si es último intento, lanzar error
                if attempt == self.max_retries - 1:
                    raise

            except httpx.RequestError as e:
                self.logger.error(
                    "supplier_request_error",
                    error=str(e),
                    endpoint=endpoint,
                    attempt=attempt + 1,
                )

                if attempt == self.max_retries - 1:
                    raise

    @abstractmethod
    async def _authenticate(self) -> dict[str, str]:
        """
        Obtener headers de autenticación
        Cada supplier implementa su método (OAuth2, Basic, API Key, etc)

        Returns:
            dict con headers de autenticación
        """
        pass

    @abstractmethod
    async def search_availability(
        self,
        pickup_office_code: str,
        dropoff_office_code: str,
        pickup_datetime,
        dropoff_datetime,
        driver_age: int | None = None,
    ) -> list[dict[str, Any]]:
        """Implementación específica por supplier"""
        pass

    @abstractmethod
    async def create_reservation(
        self,
        reservation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Implementación específica por supplier"""
        pass

    async def confirm_reservation(
        self,
        supplier_reservation_code: str
    ) -> dict[str, Any]:
        """
        Confirmar reserva (solo si el supplier usa flujo de 2 pasos)
        Por defecto no hace nada (override si es necesario)
        """
        return {
            'confirmation_number': supplier_reservation_code,
            'status': 'CONFIRMED',
        }

    async def get_reservation_status(
        self,
        supplier_reservation_code: str
    ) -> dict[str, Any]:
        """
        Consultar estado de reserva
        Por defecto retorna confirmada (override si es necesario)
        """
        return {
            'confirmation_number': supplier_reservation_code,
            'status': 'CONFIRMED',
            'pickup_completed': False,
            'dropoff_completed': False,
        }

    async def close(self) -> None:
        """Cerrar conexiones HTTP"""
        if self._client:
            await self._client.aclose()
            self._client = None
