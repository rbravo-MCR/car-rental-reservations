"""
Reservation Repository Implementation
Implementación concreta del repositorio de reservas
"""
from datetime import datetime

from src.domain.value_objects.reservation_status import PaymentStatus, ReservationStatus
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.contact import Contact, ContactType
from src.domain.entities.driver import Driver
from src.domain.entities.reservation import Reservation
from src.infrastructure.persistence.models import (
    ContactModel,
    DriverModel,
    ReservationModel,
)


class SQLAlchemyReservationRepository:
    """Implementación de ReservationRepository con SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, reservation_id: int) -> Reservation | None:
        """Obtener reserva por ID"""
        stmt = (
            select(ReservationModel)
            .where(ReservationModel.id == reservation_id)
            .options(
                selectinload(ReservationModel.drivers),
                selectinload(ReservationModel.contacts),
                selectinload(ReservationModel.pricing_items),
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_by_code(self, reservation_code: str) -> Reservation | None:
        """Obtener reserva por código"""
        stmt = (
            select(ReservationModel)
            .where(ReservationModel.reservation_code == reservation_code)
            .options(
                selectinload(ReservationModel.drivers),
                selectinload(ReservationModel.contacts),
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def exists_by_code(self, reservation_code: str) -> bool:
        """Verificar si existe código de reserva"""
        stmt = select(ReservationModel.id).where(
            ReservationModel.reservation_code == reservation_code
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def save(self, reservation: Reservation) -> Reservation:
        """Guardar reserva nueva (INSERT)"""
        # Crear model de reserva
        model = ReservationModel(
            reservation_code=reservation.reservation_code,
            app_customer_id=reservation.app_customer_id,
            corporate_account_id=reservation.corporate_account_id,
            created_by_crm_user_id=reservation.created_by_crm_user_id,
            supplier_id=reservation.supplier_id,
            pickup_office_id=reservation.pickup_office_id,
            dropoff_office_id=reservation.dropoff_office_id,
            car_category_id=reservation.car_category_id,
            supplier_car_product_id=reservation.supplier_car_product_id,
            pickup_datetime=reservation.pickup_datetime,
            dropoff_datetime=reservation.dropoff_datetime,
            rental_days=reservation.rental_days,
            currency_code=reservation.currency_code,
            public_price_total=reservation.public_price_total,
            supplier_cost_total=reservation.supplier_cost_total,
            discount_total=reservation.discount_total,
            taxes_total=reservation.taxes_total,
            fees_total=reservation.fees_total,
            commission_total=reservation.commission_total,
            cashback_earned_amount=reservation.cashback_earned_amount,
            status=reservation.status.value,
            payment_status=reservation.payment_status.value,
            sales_channel_id=reservation.sales_channel_id,
            traffic_source_id=reservation.traffic_source_id,
            marketing_campaign_id=reservation.marketing_campaign_id,
            affiliate_id=reservation.affiliate_id,
            booking_device=reservation.booking_device,
            customer_ip=reservation.customer_ip,
            customer_user_agent=reservation.customer_user_agent,
            utm_source=reservation.utm_source,
            utm_medium=reservation.utm_medium,
            utm_campaign=reservation.utm_campaign,
            utm_term=reservation.utm_term,
            utm_content=reservation.utm_content,
            supplier_name_snapshot=reservation.supplier_name_snapshot,
            pickup_office_code_snapshot=reservation.pickup_office_code_snapshot,
            pickup_office_name_snapshot=reservation.pickup_office_name_snapshot,
            dropoff_office_code_snapshot=reservation.dropoff_office_code_snapshot,
            dropoff_office_name_snapshot=reservation.dropoff_office_name_snapshot,
            pickup_city_name_snapshot=reservation.pickup_city_name_snapshot,
            pickup_country_name_snapshot=reservation.pickup_country_name_snapshot,
            car_acriss_code_snapshot=reservation.car_acriss_code_snapshot,
            car_category_name_snapshot=reservation.car_category_name_snapshot,
            supplier_reservation_code=reservation.supplier_reservation_code,
            supplier_confirmed_at=reservation.supplier_confirmed_at,
        )

        self.session.add(model)
        await self.session.flush()

        # Guardar drivers
        for driver in reservation.drivers:
            driver_model = DriverModel(
                reservation_id=model.id,
                app_customer_id=driver.app_customer_id,
                is_primary_driver=driver.is_primary_driver,
                first_name=driver.first_name,
                last_name=driver.last_name,
                email=driver.email,
                phone=driver.phone,
                date_of_birth=driver.date_of_birth,
                driver_license_number=driver.driver_license_number,
                driver_license_country=driver.driver_license_country,
            )
            self.session.add(driver_model)

        # Guardar contacts
        for contact in reservation.contacts:
            contact_model = ContactModel(
                reservation_id=model.id,
                contact_type=contact.contact_type.value,
                full_name=contact.full_name,
                email=contact.email,
                phone=contact.phone,
            )
            self.session.add(contact_model)

        await self.session.flush()

        # Actualizar entity con ID generado
        reservation.id = model.id

        return reservation

    async def update(self, reservation: Reservation) -> Reservation:
        """Actualizar reserva existente"""
        stmt = select(ReservationModel).where(
            ReservationModel.id == reservation.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        # Actualizar campos (solo los que pueden cambiar)
        model.status = reservation.status.value
        model.payment_status = reservation.payment_status.value
        model.supplier_reservation_code = reservation.supplier_reservation_code
        model.supplier_confirmed_at = reservation.supplier_confirmed_at
        model.lock_version = reservation.lock_version + 1
        model.updated_at = datetime.utcnow()

        await self.session.flush()

        return reservation

    async def list_by_customer(
        self,
        customer_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Reservation]:
        """Listar reservas de un cliente"""
        stmt = (
            select(ReservationModel)
            .where(ReservationModel.app_customer_id == customer_id)
            .order_by(ReservationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(ReservationModel.drivers),
                selectinload(ReservationModel.contacts),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        supplier_id: int | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Reservation]:
        """Listar reservas en un rango de fechas"""
        conditions = [
            ReservationModel.pickup_datetime >= start_date,
            ReservationModel.pickup_datetime <= end_date,
        ]

        if supplier_id:
            conditions.append(ReservationModel.supplier_id == supplier_id)

        stmt = (
            select(ReservationModel)
            .where(and_(*conditions))
            .order_by(ReservationModel.pickup_datetime.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def check_availability(
        self,
        car_category_id: int,
        supplier_id: int,
        pickup_datetime: datetime,
        dropoff_datetime: datetime
    ) -> bool:
        """
        Verificar disponibilidad (no hay overlaps)
        Retorna True si está disponible (NO hay conflictos)
        """
        # Buscar reservas que hagan overlap
        stmt = select(ReservationModel.id).where(
            and_(
                ReservationModel.car_category_id == car_category_id,
                ReservationModel.supplier_id == supplier_id,
                ReservationModel.status.in_(
                    ['PENDING', 'ON_REQUEST', 'CONFIRMED']),
                # Overlap condition: (start1 < end2) AND (end1 > start2)
                ReservationModel.pickup_datetime < dropoff_datetime,
                ReservationModel.dropoff_datetime > pickup_datetime,
            )
        ).limit(1)

        result = await self.session.execute(stmt)
        conflict = result.scalar_one_or_none()

        # Si NO hay conflicto, está disponible
        return conflict is None

    def _to_entity(self, model: ReservationModel) -> Reservation:
        """Convertir ORM model a domain entity"""
        reservation = Reservation(
            id=model.id,
            reservation_code=model.reservation_code,
            app_customer_id=model.app_customer_id,
            corporate_account_id=model.corporate_account_id,
            created_by_crm_user_id=model.created_by_crm_user_id,
            supplier_id=model.supplier_id,
            pickup_office_id=model.pickup_office_id,
            dropoff_office_id=model.dropoff_office_id,
            car_category_id=model.car_category_id,
            supplier_car_product_id=model.supplier_car_product_id,
            pickup_datetime=model.pickup_datetime,
            dropoff_datetime=model.dropoff_datetime,
            rental_days=model.rental_days,
            currency_code=model.currency_code,
            public_price_total=model.public_price_total,
            supplier_cost_total=model.supplier_cost_total,
            discount_total=model.discount_total,
            taxes_total=model.taxes_total,
            fees_total=model.fees_total,
            commission_total=model.commission_total,
            cashback_earned_amount=model.cashback_earned_amount,
            status=ReservationStatus(model.status),
            payment_status=PaymentStatus(model.payment_status),
            sales_channel_id=model.sales_channel_id,
            traffic_source_id=model.traffic_source_id,
            marketing_campaign_id=model.marketing_campaign_id,
            affiliate_id=model.affiliate_id,
            booking_device=model.booking_device,
            customer_ip=model.customer_ip,
            customer_user_agent=model.customer_user_agent,
            utm_source=model.utm_source,
            utm_medium=model.utm_medium,
            utm_campaign=model.utm_campaign,
            utm_term=model.utm_term,
            utm_content=model.utm_content,
            supplier_name_snapshot=model.supplier_name_snapshot,
            pickup_office_code_snapshot=model.pickup_office_code_snapshot,
            pickup_office_name_snapshot=model.pickup_office_name_snapshot,
            dropoff_office_code_snapshot=model.dropoff_office_code_snapshot,
            dropoff_office_name_snapshot=model.dropoff_office_name_snapshot,
            pickup_city_name_snapshot=model.pickup_city_name_snapshot,
            pickup_country_name_snapshot=model.pickup_country_name_snapshot,
            car_acriss_code_snapshot=model.car_acriss_code_snapshot,
            car_category_name_snapshot=model.car_category_name_snapshot,
            created_at=model.created_at,
            updated_at=model.updated_at,
            lock_version=model.lock_version,
            cancelled_at=model.cancelled_at,
            cancel_reason=model.cancel_reason,
            supplier_reservation_code=model.supplier_reservation_code,
            supplier_confirmed_at=model.supplier_confirmed_at,
        )

        # Convertir drivers
        for driver_model in model.drivers:
            driver = Driver(
                id=driver_model.id,
                reservation_id=driver_model.reservation_id,
                app_customer_id=driver_model.app_customer_id,
                is_primary_driver=driver_model.is_primary_driver,
                first_name=driver_model.first_name,
                last_name=driver_model.last_name,
                email=driver_model.email,
                phone=driver_model.phone,
                date_of_birth=driver_model.date_of_birth,
                driver_license_number=driver_model.driver_license_number,
                driver_license_country=driver_model.driver_license_country,
            )
            reservation.drivers.append(driver)

        # Convertir contacts
        for contact_model in model.contacts:
            contact = Contact(
                id=contact_model.id,
                reservation_id=contact_model.reservation_id,
                contact_type=ContactType(contact_model.contact_type),
                full_name=contact_model.full_name,
                email=contact_model.email,
                phone=contact_model.phone,
            )
            reservation.contacts.append(contact)

        return reservation
