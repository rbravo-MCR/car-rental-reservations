"""
Search Availability Use Case
Buscar disponibilidad de vehículos
"""
import structlog

from application.dto.availability_dto import AvailabilityResultDTO, AvailabilitySearchDTO
from application.ports.supplier_gateway import SupplierGateway
from application.ports.unit_of_work import UnitOfWork

logger = structlog.get_logger()


class SearchAvailabilityUseCase:
    """
    Use Case: Buscar disponibilidad de vehículos

    Busca en suppliers externos y retorna lista de vehículos disponibles
    """

    def __init__(
        self,
        uow: UnitOfWork,
        supplier_gateway: SupplierGateway,
    ):
        self.uow = uow
        self.supplier_gateway = supplier_gateway

    async def execute(
        self,
        dto: AvailabilitySearchDTO
    ) -> list[AvailabilityResultDTO]:
        """Ejecutar búsqueda"""

        logger.info(
            "availability_search_started",
            pickup_office=dto.pickup_office_id,
            pickup_datetime=dto.pickup_datetime.isoformat(),
        )

        async with self.uow:
            # Obtener oficinas para códigos
            pickup_office = await self.uow.offices.get_by_id(dto.pickup_office_id)
            dropoff_office = await self.uow.offices.get_by_id(dto.dropoff_office_id)

            if not pickup_office or not dropoff_office:
                logger.error("invalid_offices")
                return []

            # Buscar en supplier
            try:
                vehicles = await self.supplier_gateway.search_availability(
                    pickup_office_code=pickup_office['code'],
                    dropoff_office_code=dropoff_office['code'],
                    pickup_datetime=dto.pickup_datetime,
                    dropoff_datetime=dto.dropoff_datetime,
                    driver_age=dto.driver_age,
                )

                # Convertir a DTOs
                results = []
                for vehicle in vehicles:
                    results.append(AvailabilityResultDTO(
                        supplier_id=self.supplier_gateway.supplier_id,
                        supplier_name=self.supplier_gateway.supplier_name,
                        vehicle_id=vehicle.get('vehicle_id', 0),
                        vehicle_name=vehicle.get('vehicle_name', ''),
                        acriss_code=vehicle.get('acriss_code', ''),
                        car_category_id=vehicle.get('car_category_id', 0),
                        car_category_name=vehicle.get('car_category_name', ''),
                        total_price=vehicle.get('total_price', 0),
                        daily_rate=vehicle.get('daily_rate', 0),
                        currency_code=vehicle.get('currency_code', 'USD'),
                        transmission=vehicle.get('transmission'),
                        doors=vehicle.get('doors'),
                        seats=vehicle.get('seats'),
                        air_conditioning=vehicle.get('air_conditioning', True),
                        available=True,
                        supplier_product_code=vehicle.get(
                            'supplier_product_code'),
                    ))

                logger.info(
                    "availability_search_completed",
                    results_count=len(results),
                )

                return results

            except Exception as e:
                logger.error(
                    "availability_search_failed",
                    error=str(e),
                )
                return []




# ✅ USE CASES COMPLETADOS
'''
Has creado ** 5 archivos de use cases ** (32-36):
- ✅ Create Reservation(completo con pago y supplier)
- ✅ Get Reservation
- ✅ List Reservations
- ✅ Search Availability

'''

# 🎯 RESUMEN DE APPLICATION LAYER
'''
**Total: 15 archivos**
- 6 Ports(interfaces)
- 4 DTOs
- 5 Use Cases

'''

# 📊 PROGRESO TOTAL
'''
✅ Config:        5 archivos
✅ Domain:       21 archivos
✅ Application:  15 archivos
───────────────────────────
Total:          41 archivos
'''
