"""
Reservation Aggregate Root
Entidad principal del dominio
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.domain.events.reservation_confirmed import ReservationConfirmed
from src.domain.events.reservation_created import ReservationCreated
from src.domain.exceptions.reservation_errors import InvalidStateTransitionError
from src.domain.value_objects.reservation_status import PaymentStatus, ReservationStatus

from src.domain.entities.contact import Contact, ContactType
from src.domain.entities.driver import Driver
from src.domain.entities.pricing_item import PricingItem


@dataclass
class Reservation:
    """
    Aggregate Root: Reserva
    Controla todas las operaciones sobre una reserva
    """

    # Identity
    id: int | None = None
    reservation_code: str = ""

    # Relationships
    app_customer_id: int | None = None
    corporate_account_id: int | None = None
    created_by_crm_user_id: int | None = None
    supplier_id: int = 0
    pickup_office_id: int = 0
    dropoff_office_id: int = 0
    car_category_id: int = 0
    supplier_car_product_id: int | None = None

    # Dates
    pickup_datetime: datetime = field(default_factory=datetime.utcnow)
    dropoff_datetime: datetime = field(default_factory=datetime.utcnow)
    rental_days: int = 1

    # Pricing
    currency_code: str = "USD"
    public_price_total: Decimal = Decimal("0.00")
    supplier_cost_total: Decimal = Decimal("0.00")
    discount_total: Decimal = Decimal("0.00")
    taxes_total: Decimal = Decimal("0.00")
    fees_total: Decimal = Decimal("0.00")
    commission_total: Decimal = Decimal("0.00")
    cashback_earned_amount: Decimal = Decimal("0.00")

    # Status
    status: ReservationStatus = ReservationStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID

    # Marketing & Attribution
    sales_channel_id: int = 0
    traffic_source_id: int | None = None
    marketing_campaign_id: int | None = None
    affiliate_id: int | None = None
    booking_device: str | None = None
    customer_ip: str | None = None
    customer_user_agent: str | None = None

    # UTM Parameters
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None

    # Snapshots (datos históricos)
    supplier_name_snapshot: str | None = None
    pickup_office_code_snapshot: str | None = None
    pickup_office_name_snapshot: str | None = None
    dropoff_office_code_snapshot: str | None = None
    dropoff_office_name_snapshot: str | None = None
    pickup_city_name_snapshot: str | None = None
    pickup_country_name_snapshot: str | None = None
    car_acriss_code_snapshot: str | None = None
    car_category_name_snapshot: str | None = None

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    lock_version: int = 0

    # Cancellation (manejado por otra app, pero existe en DB)
    cancelled_at: datetime | None = None
    cancel_reason: str | None = None

    # Supplier confirmation
    supplier_reservation_code: str | None = None
    supplier_confirmed_at: datetime | None = None

    # Aggregated entities (no persistidos directamente, se manejan por repositorios)
    drivers: list[Driver] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    pricing_items: list[PricingItem] = field(default_factory=list)

    # Domain events
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Convertir decimales"""
        decimal_fields = [
            'public_price_total', 'supplier_cost_total', 'discount_total',
            'taxes_total', 'fees_total', 'commission_total', 'cashback_earned_amount'
        ]
        for field_name in decimal_fields:
            value = getattr(self, field_name)
            if not isinstance(value, Decimal):
                setattr(self, field_name, Decimal(str(value)))

    @classmethod
    def create(
        cls,
        reservation_code: str,
        supplier_id: int,
        pickup_office_id: int,
        dropoff_office_id: int,
        car_category_id: int,
        supplier_car_product_id: int,
        pickup_datetime: datetime,
        dropoff_datetime: datetime,
        rental_days: int,
        currency_code: str,
        public_price_total: Decimal,
        supplier_cost_total: Decimal,
        status: ReservationStatus,
        payment_status: PaymentStatus,
        sales_channel_id: int = 1,
    ) -> "Reservation":
        """Factory method para crear reserva"""
        reservation = cls(
            reservation_code=reservation_code,
            supplier_id=supplier_id,
            pickup_office_id=pickup_office_id,
            dropoff_office_id=dropoff_office_id,
            car_category_id=car_category_id,
            supplier_car_product_id=supplier_car_product_id,
            pickup_datetime=pickup_datetime,
            dropoff_datetime=dropoff_datetime,
            rental_days=rental_days,
            currency_code=currency_code,
            public_price_total=public_price_total,
            supplier_cost_total=supplier_cost_total,
            status=status,
            payment_status=payment_status,
            sales_channel_id=sales_channel_id,
        )

        # Registrar evento
        reservation._add_event(ReservationCreated(
            aggregate_id=None,  # Se asignará después del save
            reservation_code=reservation_code,
            pickup_datetime=pickup_datetime,
            total_amount=str(public_price_total),
            currency_code=currency_code,
        ))

        return reservation

    def add_driver(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        is_primary: bool = True,
        **kwargs
    ) -> Driver:
        """Agregar conductor"""
        driver = Driver(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            is_primary_driver=is_primary,
            **kwargs
        )
        self.drivers.append(driver)
        return driver

    def add_contact(
        self,
        contact_type: str,
        full_name: str,
        email: str,
        phone: str | None = None,
    ) -> Contact:
        """Agregar contacto"""
        contact = Contact(
            contact_type=ContactType(contact_type),
            full_name=full_name,
            email=email,
            phone=phone,
        )
        self.contacts.append(contact)
        return contact

    def confirm_with_supplier(
        self,
        supplier_reservation_code: str,
        supplier_confirmed_at: datetime,
    ) -> None:
        """Confirmar reserva con supplier"""
        # Validar transición de estado
        if not self._can_transition_to(ReservationStatus.CONFIRMED):
            raise InvalidStateTransitionError(
                self.status.value, ReservationStatus.CONFIRMED.value)

        self.supplier_reservation_code = supplier_reservation_code
        self.supplier_confirmed_at = supplier_confirmed_at
        self.status = ReservationStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

        # Registrar evento
        self._add_event(ReservationConfirmed(
            aggregate_id=self.id,
            reservation_code=self.reservation_code,
            supplier_reservation_code=supplier_reservation_code,
            supplier_name=self.supplier_name_snapshot or "",
            customer_email=self.contacts[0].email if self.contacts else "",
        ))

    def mark_as_paid(self) -> None:
        """Marcar como pagada"""
        self.payment_status = PaymentStatus.PAID
        self.updated_at = datetime.utcnow()

    def _can_transition_to(self, new_status: ReservationStatus) -> bool:
        """Validar si puede transicionar a nuevo estado"""
        # Importar aquí para evitar ciclo de importación
        from domain.services.state_machine import can_transition
        return can_transition(self.status, new_status)

    def _add_event(self, event) -> None:
        """Agregar evento de dominio"""
        self._events.append(event)

    def clear_events(self) -> list:
        """Obtener y limpiar eventos (para publicarlos después del commit)"""
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def is_confirmed(self) -> bool:
        """Verifica si está confirmada"""
        return self.status == ReservationStatus.CONFIRMED

    @property
    def is_paid(self) -> bool:
        """Verifica si está pagada"""
        return self.payment_status == PaymentStatus.PAID
