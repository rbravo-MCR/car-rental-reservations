"""
Supplier Factory
Factory pattern para crear instancias de suppliers dinámicamente
"""
# Importar otros clientes cuando los crees
# from src.infrastructure.external.suppliers.europcar_client import EuropcarClient
from src.config.settings import get_settings
from src.infrastructure.external.suppliers.base_supplier import BaseSupplierClient
from src.infrastructure.external.suppliers.localiza_client import LocalizaClient

settings = get_settings()


class SupplierFactory:
    """
    Factory para crear instancias de suppliers
    Mapea supplier_id a la implementación correcta
    """

    def __init__(self) -> None:
        self._suppliers: dict[int, BaseSupplierClient] = {}

    async def get_supplier(self, supplier_id: int) -> BaseSupplierClient:
        """
        Retorna instancia del supplier (singleton por supplier_id)
        Args:
            supplier_id: ID del supplier en BD

        Returns:
            BaseSupplierClient: Instancia del cliente

        Raises:
            ValueError: Si supplier_id no está configurado
        """
        # Si ya existe, retornar (singleton)
        if supplier_id in self._suppliers:
            return self._suppliers[supplier_id]

        # Crear nueva instancia según supplier_id
        # En producción esto vendría de una tabla de configuración
        # Por ahora, hardcodeamos algunos ejemplos

        if supplier_id == 1:  # LOCALIZA
            client = LocalizaClient(supplier_id=supplier_id)

        # elif supplier_id == 2:  # Europcar
        #     client = EuropcarClient(supplier_id=supplier_id)

        # elif supplier_id == 3:  # Rently Network
        #     client = RentlyNetworkClient(supplier_id=supplier_id)

        else:
            raise ValueError(
                f"Supplier {supplier_id} not configured. "
                f"Add implementation in SupplierFactory."
            )

        # Guardar en cache
        self._suppliers[supplier_id] = client

        return client

    async def close_all(self) -> None:
        """Cerrar todas las conexiones de suppliers"""
        for client in self._suppliers.values():
            await client.close()

        self._suppliers.clear()
