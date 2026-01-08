"""
LOCALIZA Supplier Client
Implementación específica para LOCALIZA (Brasil)
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from src.config.settings import get_settings

from src.infrastructure.external.suppliers.base_supplier import BaseSupplierClient

settings = get_settings()


class LocalizaClient(BaseSupplierClient):
    """Cliente para LOCALIZA (Brasil) - OAuth2"""

    def __init__(self, supplier_id: int):
        super().__init__(
            supplier_id=supplier_id,
            supplier_name="LOCALIZA",
            base_url=settings.localiza_base_url,
            timeout=30,
        )
        self.api_key = settings.localiza_api_key
        self.api_secret = settings.localiza_api_secret
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    async def _authenticate(self) -> dict[str, str]:
        """OAuth2 Client Credentials Flow"""
        # Si token está vigente, reutilizar
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return {"Authorization": f"Bearer {self._access_token}"}

        # Obtener nuevo token
        self.logger.info("localiza_refreshing_token")

        response = await self._request(
            "POST",
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            }
        )

        data = response.json()
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        self.logger.info("localiza_token_refreshed", expires_in=expires_in)

        return {"Authorization": f"Bearer {self._access_token}"}

    async def search_availability(
        self,
        pickup_office_code: str,
        dropoff_office_code: str,
        pickup_datetime: datetime,
        dropoff_datetime: datetime,
        driver_age: int | None = None,
    ) -> list[dict[str, Any]]:
        """Buscar disponibilidad en LOCALIZA"""
        headers = await self._authenticate()

        payload = {
            "pickupLocation": pickup_office_code,
            "dropoffLocation": dropoff_office_code,
            "pickupDate": pickup_datetime.isoformat(),
            "dropoffDate": dropoff_datetime.isoformat(),
            "driverAge": driver_age or 25,
        }

        response = await self._request(
            "POST",
            "/availability/search",
            headers=headers,
            json=payload,
        )

        data = response.json()

        # Mapear respuesta de LOCALIZA a formato interno
        results = []
        for vehicle in data.get("vehicles", []):
            results.append({
                'vehicle_id': 0,  # Se mapeará después
                'vehicle_name': vehicle.get('model', ''),
                'acriss_code': vehicle.get('acrissCode', ''),
                'car_category_id': 0,  # Se mapeará después
                'car_category_name': vehicle.get('category', ''),
                'total_price': Decimal(str(vehicle.get('totalPrice', 0))),
                'daily_rate': Decimal(str(vehicle.get('dailyRate', 0))),
                'currency_code': vehicle.get('currency', 'BRL'),
                'transmission': vehicle.get('transmission'),
                'doors': vehicle.get('doors'),
                'seats': vehicle.get('seats'),
                'air_conditioning': vehicle.get('airConditioning', True),
                'supplier_product_code': vehicle.get('rateCode'),
            })

        return results

    async def create_reservation(
        self,
        reservation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Crear reserva en LOCALIZA"""
        headers = await self._authenticate()

        driver = reservation_data['driver']

        payload = {
            "rateCode": reservation_data.get('supplier_product_code'),
            "pickupLocation": reservation_data['pickup_office_code'],
            "dropoffLocation": reservation_data['dropoff_office_code'],
            "pickupDateTime": reservation_data['pickup_datetime'].isoformat(),
            "dropoffDateTime": reservation_data['dropoff_datetime'].isoformat(),
            "driver": {
                "firstName": driver['first_name'],
                "lastName": driver['last_name'],
                "email": driver['email'],
                "phone": driver['phone'],
            },
            "referenceNumber": reservation_data.get('internal_code'),
        }

        response = await self._request(
            "POST",
            "/reservations",
            headers=headers,
            json=payload,
        )

        result = response.json()

        return {
            'confirmation_number': result['confirmationNumber'],
            'status': 'CONFIRMED',
            'total_price': Decimal(str(result.get('totalPrice', 0))),
            'currency_code': result.get('currency', 'BRL'),
        }
