"""
SQLAlchemy Models (ORM)
Mapeo de tablas MySQL a clases Python
"""

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from infrastructure.persistence.database import Base


class ReservationModel(Base):
    """Modelo ORM para tabla reservations"""
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_code = Column(String(50), unique=True,
                              nullable=False, index=True)

    # Relationships
    app_customer_id = Column(BigInteger, ForeignKey(
        "app_customers.id"), nullable=True)
    corporate_account_id = Column(BigInteger, ForeignKey(
        "corporate_accounts.id"), nullable=True)
    created_by_crm_user_id = Column(
        BigInteger, ForeignKey("crm_users.id"), nullable=True)
    supplier_id = Column(BigInteger, ForeignKey(
        "suppliers.id"), nullable=False)
    pickup_office_id = Column(
        BigInteger, ForeignKey("offices.id"), nullable=False)
    dropoff_office_id = Column(
        BigInteger, ForeignKey("offices.id"), nullable=False)
    car_category_id = Column(BigInteger, ForeignKey(
        "car_categories.id"), nullable=False)
    supplier_car_product_id = Column(BigInteger, ForeignKey(
        "supplier_car_products.id"), nullable=True)

    # Dates
    pickup_datetime = Column(DateTime, nullable=False, index=True)
    dropoff_datetime = Column(DateTime, nullable=False)
    rental_days = Column(SmallInteger, nullable=False)

    # Pricing
    currency_code = Column(String(3), nullable=False)
    public_price_total = Column(Numeric(12, 2), nullable=False)
    supplier_cost_total = Column(Numeric(12, 2), nullable=False)
    discount_total = Column(Numeric(12, 2), nullable=False, default=0)
    taxes_total = Column(Numeric(12, 2), nullable=False, default=0)
    fees_total = Column(Numeric(12, 2), nullable=False, default=0)
    commission_total = Column(Numeric(12, 2), nullable=False, default=0)
    cashback_earned_amount = Column(Numeric(12, 2), nullable=False, default=0)

    # Status
    status = Column(
        Enum('PENDING', 'ON_REQUEST', 'CONFIRMED', 'CANCELLED',
             'NO_SHOW', 'IN_PROGRESS', 'COMPLETED', name='reservation_status'),
        nullable=False,
        default='PENDING',
        index=True
    )
    payment_status = Column(
        Enum('UNPAID', 'PAID', 'PARTIALLY_REFUNDED', 'REFUNDED',
             'CHARGEBACK', name='payment_status'),
        nullable=False,
        default='UNPAID',
        index=True
    )

    # Marketing
    sales_channel_id = Column(BigInteger, ForeignKey(
        "sales_channels.id"), nullable=False)
    traffic_source_id = Column(BigInteger, ForeignKey(
        "traffic_sources.id"), nullable=True)
    marketing_campaign_id = Column(BigInteger, ForeignKey(
        "marketing_campaigns.id"), nullable=True)
    affiliate_id = Column(BigInteger, ForeignKey(
        "affiliates.id"), nullable=True)
    booking_device = Column(
        Enum('DESKTOP', 'MOBILE_WEB', 'IOS_APP', 'ANDROID_APP', 'CALL_CENTER',
             name='booking_device'),
        nullable=True
    )
    customer_ip = Column(String(45), nullable=True)
    customer_user_agent = Column(String(500), nullable=True)

    # UTM
    utm_source = Column(String(150), nullable=True)
    utm_medium = Column(String(150), nullable=True)
    utm_campaign = Column(String(255), nullable=True)
    utm_term = Column(String(255), nullable=True)
    utm_content = Column(String(255), nullable=True)

    # Snapshots
    supplier_name_snapshot = Column(String(255), nullable=True)
    pickup_office_code_snapshot = Column(String(50), nullable=True)
    pickup_office_name_snapshot = Column(String(255), nullable=True)
    dropoff_office_code_snapshot = Column(String(50), nullable=True)
    dropoff_office_name_snapshot = Column(String(255), nullable=True)
    pickup_city_name_snapshot = Column(String(150), nullable=True)
    pickup_country_name_snapshot = Column(String(150), nullable=True)
    car_acriss_code_snapshot = Column(String(10), nullable=True)
    car_category_name_snapshot = Column(String(150), nullable=True)

    # Audit
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())
    lock_version = Column(Integer, nullable=False, default=0)

    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(String(255), nullable=True)

    # Supplier confirmation
    supplier_reservation_code = Column(String(64), nullable=True)
    supplier_confirmed_at = Column(DateTime, nullable=True)

    # Relationships ORM
    drivers = relationship(
        "DriverModel", back_populates="reservation", lazy="selectin")
    contacts = relationship(
        "ContactModel", back_populates="reservation", lazy="selectin")
    payments = relationship(
        "PaymentModel", back_populates="reservation", lazy="selectin")
    pricing_items = relationship(
        "PricingItemModel", back_populates="reservation", lazy="selectin")

    # Índices compuestos
    __table_args__ = (
        Index('idx_res_availability', 'pickup_datetime', 'dropoff_datetime',
              'car_category_id', 'supplier_id', 'status'),
        Index('idx_res_supplier_status_pickup',
              'supplier_id', 'status', 'pickup_datetime'),
    )


class DriverModel(Base):
    """Modelo ORM para tabla reservation_drivers"""
    __tablename__ = "reservation_drivers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_id = Column(BigInteger, ForeignKey(
        "reservations.id"), nullable=False, index=True)
    app_customer_id = Column(BigInteger, ForeignKey(
        "app_customers.id"), nullable=True)
    is_primary_driver = Column(Boolean, nullable=False, default=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    driver_license_number = Column(String(100), nullable=True)
    driver_license_country = Column(String(2), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    reservation = relationship("ReservationModel", back_populates="drivers")


class ContactModel(Base):
    """Modelo ORM para tabla reservation_contacts"""
    __tablename__ = "reservation_contacts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_id = Column(BigInteger, ForeignKey(
        "reservations.id"), nullable=False, index=True)
    contact_type = Column(
        Enum('BOOKER', 'EMERGENCY', name='contact_type'),
        nullable=False,
        default='BOOKER'
    )
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    reservation = relationship("ReservationModel", back_populates="contacts")


class PaymentModel(Base):
    """Modelo ORM para tabla payments"""
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_id = Column(BigInteger, ForeignKey(
        "reservations.id"), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    provider_transaction_id = Column(String(255), nullable=True)
    method = Column(String(100), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    status = Column(
        Enum('PENDING', 'AUTHORIZED', 'CAPTURED', 'FAILED',
             'REFUNDED', 'PARTIALLY_REFUNDED', 'CHARGEBACK', name='payment_status_enum'),
        nullable=False,
        default='PENDING',
        index=True
    )
    captured_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())

    # Stripe specific
    stripe_payment_intent_id = Column(String(64), nullable=True, index=True)
    stripe_charge_id = Column(String(64), nullable=True, index=True)
    stripe_event_id = Column(String(64), nullable=True)
    amount_refunded = Column(Numeric(12, 2), nullable=False, default=0)
    fee_amount = Column(Numeric(12, 2), nullable=True)
    net_amount = Column(Numeric(12, 2), nullable=True)

    # Relationships
    reservation = relationship("ReservationModel", back_populates="payments")


class PricingItemModel(Base):
    """Modelo ORM para tabla reservation_pricing_items"""
    __tablename__ = "reservation_pricing_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_id = Column(BigInteger, ForeignKey(
        "reservations.id"), nullable=False, index=True)
    item_type = Column(
        Enum('BASE_RATE', 'TAX', 'FEE', 'EXTRA', 'INSURANCE', 'DISCOUNT', 'OTHER',
             name='pricing_item_type'),
        nullable=False
    )
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=1)
    unit_price_public = Column(Numeric(12, 2), nullable=False, default=0)
    unit_price_supplier = Column(Numeric(12, 2), nullable=False, default=0)
    total_price_public = Column(Numeric(12, 2), nullable=False, default=0)
    total_price_supplier = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    reservation = relationship(
        "ReservationModel", back_populates="pricing_items")


class OutboxEventModel(Base):
    """Modelo ORM para tabla outbox_events"""
    __tablename__ = "outbox_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(64), nullable=False)
    aggregate_type = Column(String(32), nullable=False)
    aggregate_id = Column(BigInteger, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(16), nullable=False, default='NEW', index=True)
    attempts = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(DateTime, nullable=True)
    locked_by = Column(String(64), nullable=True)
    locked_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    __table_args__ = (
        Index('idx_outbox_status_next', 'status', 'next_attempt_at'),
        Index('idx_outbox_aggregate', 'aggregate_type', 'aggregate_id'),
    )


class SupplierRequestModel(Base):
    """Modelo ORM para tabla reservation_supplier_requests"""
    __tablename__ = "reservation_supplier_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reservation_id = Column(BigInteger, ForeignKey(
        "reservations.id"), nullable=False, index=True)
    supplier_id = Column(BigInteger, ForeignKey(
        "suppliers.id"), nullable=False)
    request_type = Column(String(32), nullable=False, index=True)
    idem_key = Column(String(128), nullable=True)
    attempt = Column(Integer, nullable=False, default=0)
    status = Column(String(16), nullable=False, index=True)
    http_status = Column(SmallInteger, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(String(255), nullable=True)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    __table_args__ = (
        Index('idx_supplier_request_created',
              'supplier_id', 'status', 'created_at'),
    )


class IdempotencyKeyModel(Base):
    """Modelo ORM para tabla idempotency_keys"""
    __tablename__ = "idempotency_keys"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    scope = Column(String(32), nullable=False)
    idem_key = Column(String(128), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_json = Column(JSON, nullable=True)
    http_status = Column(SmallInteger, nullable=True)
    reference_reservation_id = Column(BigInteger, nullable=True)
    reference_customer_id = Column(BigInteger, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        Index('uq_scope_key', 'scope', 'idem_key', unique=True),
        Index('idx_idem_created', 'created_at'),
    )

# ============================================
# MODELOS DE CATÁLOGO (SUPPORT TABLES)
# ============================================


class SupplierModel(Base):
    """Modelo ORM para tabla suppliers"""
    __tablename__ = "suppliers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    website_url = Column(String(255), nullable=True)
    support_email = Column(String(255), nullable=True)
    support_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    brand_id = Column(BigInteger, nullable=True)
    country_code = Column(String(2), nullable=True)
    region_code = Column(String(20), nullable=True)
    external_supplier_code = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())


class CountryModel(Base):
    """Modelo ORM para tabla countries"""
    __tablename__ = "countries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    iso_code = Column(String(2), nullable=False, unique=True)
    iso3_code = Column(String(3), nullable=True)
    name = Column(String(150), nullable=False)
    default_currency_code = Column(String(3), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())


class CityModel(Base):
    """Modelo ORM para tabla cities"""
    __tablename__ = "cities"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    country_id = Column(BigInteger, ForeignKey("countries.id"), nullable=False)
    name = Column(String(150), nullable=False)
    state_name = Column(String(150), nullable=True)
    iata_code = Column(String(3), nullable=True)
    time_zone = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())

    # Relationships
    country = relationship("CountryModel", lazy="joined")


class OfficeModel(Base):
    """Modelo ORM para tabla offices"""
    __tablename__ = "offices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    supplier_id = Column(BigInteger, ForeignKey(
        "suppliers.id"), nullable=False)
    city_id = Column(BigInteger, ForeignKey("cities.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(
        Enum('AIRPORT', 'DOWNTOWN', 'NEIGHBORHOOD', 'PORT', 'TRAIN_STATION', 'OTHER',
             name='office_type'),
        nullable=False
    )
    iata_code = Column(String(3), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    opening_hours_json = Column(JSON, nullable=True)
    pickup_instructions = Column(Text, nullable=True)
    dropoff_instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())

    # Relationships
    city = relationship("CityModel", lazy="joined")

    __table_args__ = (
        Index('uq_offices_supplier_code', 'supplier_id', 'code', unique=True),
        Index('idx_offices_supplier_active', 'supplier_id', 'is_active'),
    )


class AppCustomerModel(Base):
    """Modelo ORM para tabla app_customers"""
    __tablename__ = "app_customers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    country_id = Column(BigInteger, ForeignKey("countries.id"), nullable=True)
    preferred_language = Column(String(10), nullable=True)
    preferred_currency = Column(String(3), nullable=True)
    marketing_opt_in = Column(Boolean, nullable=False, default=True)
    status = Column(
        Enum('ACTIVE', 'INACTIVE', 'BANNED',
             'PENDING_VERIFICATION', name='customer_status'),
        nullable=False,
        default='ACTIVE'
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False,
                        server_default=func.now(), onupdate=func.now())
