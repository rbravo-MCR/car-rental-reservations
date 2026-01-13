"""
Create Reservation Use Case
Caso de uso principal: Crear reserva con pago y confirmación de supplier
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import structlog

from src.application.dto.reservation_dto import CreateReservationDTO
from src.application.ports.payment_gateway import PaymentGateway
from src.application.ports.receipt_generator import ReceiptGenerator
from src.application.ports.supplier_gateway import SupplierGateway
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.payment import Payment
from src.domain.entities.reservation import Reservation
from src.domain.exceptions.payment_errors import PaymentFailedError
from src.domain.exceptions.reservation_errors import ReservationCreationError
from src.domain.exceptions.supplier_errors import SupplierConfirmationError
from src.domain.services.reservation_code_generator import ReservationCodeGenerator
from src.domain.value_objects.reservation_status import PaymentStatus, ReservationStatus

logger = structlog.get_logger()


@dataclass
class CreateReservationResult:
    """Resultado de crear reserva"""
    reservation_id: int
    reservation_code: str
    supplier_reservation_code: str
    status: str
    payment_status: str
    total_amount: Decimal
    currency_code: str
    receipt_url: str | None


class CreateReservationUseCase:
    """
    Use Case: Crear reserva con pago y confirmación de supplier

    Flujo:
    1. Generar código único interno
    2. Guardar reserva en BD (status: PENDING, payment: UNPAID)
    3. Procesar pago con Stripe
    4. Enviar a supplier para confirmación
    5. Actualizar reserva (status: CONFIRMED, supplier_code)
    6. Registrar eventos en outbox
    7. Generar recibo PDF
    8. Retornar resultado
    """

    def __init__(
        self,
        uow: UnitOfWork,
        supplier_gateway: SupplierGateway,
        payment_gateway: PaymentGateway,
        receipt_generator: ReceiptGenerator,
    ):
        self.uow = uow
        self.supplier_gateway = supplier_gateway
        self.payment_gateway = payment_gateway
        self.receipt_generator = receipt_generator

    async def execute(
        self,
        dto: CreateReservationDTO
    ) -> CreateReservationResult:
        """Ejecutar caso de uso"""

        logger.info(
            "create_reservation_started",
            supplier_id=dto.supplier_id,
            pickup_datetime=dto.pickup_datetime.isoformat(),
        )

        async with self.uow:
            try:
                # PASO 1: Generar código único
                reservation_code = await ReservationCodeGenerator.generate_unique(
                    self.uow.reservations
                )

                logger.info("reservation_code_generated",
                            code=reservation_code)

                # PASO 2: Obtener datos relacionados de BD
                supplier = await self.uow.suppliers.get_by_id(dto.supplier_id)
                if not supplier:
                    raise ReservationCreationError(
                        f"Supplier {dto.supplier_id} not found")

                pickup_office = await self.uow.offices.get_by_id(dto.pickup_office_id)
                dropoff_office = await self.uow.offices.get_by_id(dto.dropoff_office_id)

                if not pickup_office or not dropoff_office:
                    raise ReservationCreationError("Invalid office IDs")

                # PASO 3: Crear entidad de reserva
                reservation = Reservation.create(
                    reservation_code=reservation_code,
                    supplier_id=dto.supplier_id,
                    pickup_office_id=dto.pickup_office_id,
                    dropoff_office_id=dto.dropoff_office_id,
                    car_category_id=dto.car_category_id,
                    supplier_car_product_id=dto.vehicle_id,
                    pickup_datetime=dto.pickup_datetime,
                    dropoff_datetime=dto.dropoff_datetime,
                    rental_days=dto.rental_days,
                    currency_code=dto.currency_code,
                    public_price_total=dto.price,
                    supplier_cost_total=dto.price,  # TODO: calcular con markup
                    status=ReservationStatus.PENDING,
                    payment_status=PaymentStatus.UNPAID,
                    sales_channel_id=dto.sales_channel_id,
                )

                # Agregar snapshots (datos históricos)
                reservation.supplier_name_snapshot = supplier['name']
                reservation.pickup_office_code_snapshot = pickup_office['code']
                reservation.pickup_office_name_snapshot = pickup_office['name']
                reservation.dropoff_office_code_snapshot = dropoff_office['code']
                reservation.dropoff_office_name_snapshot = dropoff_office['name']
                reservation.car_acriss_code_snapshot = dto.acriss_code

                # Agregar driver
                reservation.add_driver(
                    first_name=dto.driver.first_name,
                    last_name=dto.driver.last_name,
                    email=dto.driver.email,
                    phone=dto.driver.phone,
                    is_primary=True,
                )

                # Agregar contacto (booker)
                reservation.add_contact(
                    contact_type="BOOKER",
                    full_name=f"{dto.driver.first_name} {dto.driver.last_name}",
                    email=dto.driver.email,
                    phone=dto.driver.phone,
                )

                # Guardar reserva en BD
                reservation = await self.uow.reservations.save(reservation)
                await self.uow.commit()

                logger.info(
                    "reservation_saved",
                    reservation_id=reservation.id,
                    code=reservation_code,
                )

                # PASO 4: Procesar pago con Stripe
                try:
                    payment_result = await self.payment_gateway.charge(
                        amount=dto.price,
                        currency=dto.currency_code,
                        payment_method_id=dto.payment_method_id,
                        description=f"Reserva {reservation_code}",
                        metadata={
                            "reservation_id": str(reservation.id),
                            "reservation_code": reservation_code,
                        }
                    )

                    if not payment_result.success:
                        raise PaymentFailedError(
                            payment_result.error_message or "Payment failed"
                        )

                    # Crear registro de pago
                    payment = Payment.create(
                        reservation_id=reservation.id,
                        provider="STRIPE",
                        provider_transaction_id=payment_result.charge_id or "",
                        stripe_payment_intent_id=payment_result.payment_intent_id,
                        amount=dto.price,
                        currency_code=dto.currency_code,
                        status=PaymentStatus.PAID,
                        method=payment_result.method,
                    )
                    payment.mark_as_captured(payment_result.charge_id or "")

                    await self.uow.payments.save(payment)

                    # Actualizar payment_status de reserva
                    reservation.mark_as_paid()
                    await self.uow.reservations.update(reservation)
                    await self.uow.commit()

                    logger.info(
                        "payment_completed",
                        reservation_id=reservation.id,
                        payment_intent_id=payment_result.payment_intent_id,
                    )

                except Exception as e:
                    logger.error(
                        "payment_failed",
                        reservation_id=reservation.id,
                        error=str(e),
                    )
                    raise PaymentFailedError(
                        f"Payment failed: {str(e)}") from e

                # PASO 5: Enviar a supplier para confirmación
                try:
                    supplier_result = await self.supplier_gateway.create_reservation(
                        reservation_data={
                            "internal_code": reservation_code,
                            "pickup_office_code": pickup_office['code'],
                            "dropoff_office_code": dropoff_office['code'],
                            "pickup_datetime": dto.pickup_datetime,
                            "dropoff_datetime": dto.dropoff_datetime,
                            "vehicle_code": dto.acriss_code,
                            "driver": {
                                "first_name": dto.driver.first_name,
                                "last_name": dto.driver.last_name,
                                "email": dto.driver.email,
                                "phone": dto.driver.phone,
                            }
                        }
                    )

                    # Log del request al supplier (ÉXITO)
                    await self.uow.supplier_requests.create(
                        reservation_id=reservation.id,
                        supplier_id=dto.supplier_id,
                        request_type="CREATE_RESERVATION",
                        status="SUCCESS",
                        response_payload=supplier_result,
                    )

                    logger.info(
                        "supplier_confirmed",
                        reservation_id=reservation.id,
                        supplier_code=supplier_result['confirmation_number'],
                    )

                except Exception as e:
                    logger.error(
                        "supplier_confirmation_failed",
                        reservation_id=reservation.id,
                        error=str(e),
                    )

                    # Log del error
                    await self.uow.supplier_requests.create(
                        reservation_id=reservation.id,
                        supplier_id=dto.supplier_id,
                        request_type="CREATE_RESERVATION",
                        status="FAILED",
                        error_message=str(e),
                    )

                    await self.uow.commit()

                    # TODO: En producción, aquí se debería iniciar reembolso
                    # Pero como cancelaciones están en otra app, solo loggeamos

                    raise SupplierConfirmationError(
                        f"Supplier confirmation failed: {str(e)}"
                    ) from e

                # PASO 6: Actualizar reserva con código del supplier
                reservation.confirm_with_supplier(
                    supplier_reservation_code=supplier_result['confirmation_number'],
                    supplier_confirmed_at=datetime.utcnow(),
                )

                await self.uow.reservations.update(reservation)

                # PASO 7: Registrar eventos en outbox
                # Obtener eventos de la entidad
                events = reservation.clear_events()

                for event in events:
                    await self.uow.outbox.create(
                        event_type=event.event_type,
                        aggregate_type="RESERVATION",
                        aggregate_id=reservation.id,
                        payload=event.payload or {},
                    )

                # Evento adicional de pago completado
                await self.uow.outbox.create(
                    event_type="PaymentCompleted",
                    aggregate_type="RESERVATION",
                    aggregate_id=reservation.id,
                    payload={
                        "reservation_code": reservation_code,
                        "payment_provider": "STRIPE",
                        "payment_id": payment.stripe_payment_intent_id or "",
                        "amount": str(payment.amount),
                        "currency_code": payment.currency_code,
                    }
                )

                await self.uow.commit()

                logger.info(
                    "reservation_completed",
                    reservation_id=reservation.id,
                    code=reservation_code,
                    supplier_code=supplier_result['confirmation_number'],
                )

                # PASO 8: Generar recibo PDF (fuera de la transacción)
                receipt_url = None
                try:
                    receipt_url = await self.receipt_generator.generate(
                        reservation=reservation,
                        payment=payment,
                        supplier_confirmation=supplier_result['confirmation_number'],
                    )
                except Exception as e:
                    # No fallar si el PDF falla
                    logger.warning(
                        "receipt_generation_failed",
                        reservation_id=reservation.id,
                        error=str(e),
                    )

                # PASO 9: Retornar resultado
                return CreateReservationResult(
                    reservation_id=reservation.id,
                    reservation_code=reservation_code,
                    supplier_reservation_code=supplier_result['confirmation_number'],
                    status=reservation.status.value,
                    payment_status=reservation.payment_status.value,
                    total_amount=reservation.public_price_total,
                    currency_code=reservation.currency_code,
                    receipt_url=receipt_url,
                )

            except (PaymentFailedError, SupplierConfirmationError):
                # Errores esperados, rollback y re-raise
                await self.uow.rollback()
                raise

            except Exception as e:
                # Errores inesperados
                await self.uow.rollback()
                logger.error("reservation_creation_failed", error=str(e))
                raise ReservationCreationError(
                    f"Failed to create reservation: {str(e)}"
                ) from e
