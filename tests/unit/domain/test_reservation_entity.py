"""
Unit tests for Reservation aggregate root
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.domain.entities.reservation import Reservation
from src.domain.exceptions.reservation_errors import InvalidStateTransitionError
from src.domain.value_objects.reservation_status import PaymentStatus, ReservationStatus


class TestReservationCreation:
    """Test Reservation entity creation"""

    def test_create_valid_reservation(self) -> None:
        """Test creating a valid reservation"""
        reservation = Reservation.create(
            reservation_code="RES-001",
            supplier_id=1,
            pickup_office_id=1,
            dropoff_office_id=1,
            car_category_id=1,
            supplier_car_product_id=1,
            pickup_datetime=datetime.utcnow(),
            dropoff_datetime=datetime.utcnow() + timedelta(days=3),
            rental_days=3,
            currency_code="USD",
            public_price_total=Decimal("300.00"),
            supplier_cost_total=Decimal("250.00"),
            status=ReservationStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
        )

        assert reservation.reservation_code == "RES-001"
        assert reservation.rental_days == 3
        assert reservation.public_price_total == Decimal("300.00")
        assert reservation.status == ReservationStatus.PENDING
        assert reservation.payment_status == PaymentStatus.UNPAID

    def test_create_reservation_generates_event(self) -> None:
        """Test creating reservation generates ReservationCreated event"""
        reservation = Reservation.create(
            reservation_code="RES-002",
            supplier_id=1,
            pickup_office_id=1,
            dropoff_office_id=1,
            car_category_id=1,
            supplier_car_product_id=1,
            pickup_datetime=datetime.utcnow(),
            dropoff_datetime=datetime.utcnow() + timedelta(days=1),
            rental_days=1,
            currency_code="USD",
            public_price_total=Decimal("100.00"),
            supplier_cost_total=Decimal("90.00"),
            status=ReservationStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
        )

        events = reservation.clear_events()

        assert len(events) == 1
        # Check it's a ReservationCreated event
        assert hasattr(events[0], "reservation_code")
        assert events[0].reservation_code == "RES-002"

    def test_decimal_conversion_in_post_init(self) -> None:
        """Test that __post_init__ converts float to Decimal"""
        reservation = Reservation(
            reservation_code="RES-003",
            supplier_id=1,
            pickup_office_id=1,
            dropoff_office_id=1,
            car_category_id=1,
            public_price_total=100.50,  # Pass as float
            supplier_cost_total=90.00,
        )

        assert isinstance(reservation.public_price_total, Decimal)
        assert isinstance(reservation.supplier_cost_total, Decimal)
        assert reservation.public_price_total == Decimal("100.50")


class TestAddDriver:
    """Test adding drivers to reservation"""

    def test_add_primary_driver(self) -> None:
        """Test adding primary driver"""
        reservation = Reservation(reservation_code="RES-004")

        driver = reservation.add_driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            is_primary=True,
        )

        assert len(reservation.drivers) == 1
        assert driver.first_name == "John"
        assert driver.last_name == "Doe"
        assert driver.is_primary_driver is True

    def test_add_additional_driver(self) -> None:
        """Test adding additional driver"""
        reservation = Reservation(reservation_code="RES-005")

        reservation.add_driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            is_primary=True,
        )
        reservation.add_driver(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+0987654321",
            is_primary=False,
        )

        assert len(reservation.drivers) == 2
        assert reservation.drivers[1].first_name == "Jane"
        assert reservation.drivers[1].is_primary_driver is False

    def test_add_driver_with_extra_fields(self) -> None:
        """Test adding driver with optional fields via kwargs"""
        reservation = Reservation(reservation_code="RES-006")

        driver = reservation.add_driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            date_of_birth="1990-01-01",
            driver_license_number="DL123456",
        )

        assert driver.date_of_birth == "1990-01-01"
        assert driver.driver_license_number == "DL123456"


class TestAddContact:
    """Test adding contacts to reservation"""

    def test_add_booker_contact(self) -> None:
        """Test adding booker contact"""
        reservation = Reservation(reservation_code="RES-007")

        contact = reservation.add_contact(
            contact_type="BOOKER",
            full_name="John Doe",
            email="john@example.com",
            phone="+1234567890",
        )

        assert len(reservation.contacts) == 1
        assert contact.full_name == "John Doe"
        assert contact.contact_type.value == "BOOKER"

    def test_add_emergency_contact(self) -> None:
        """Test adding emergency contact"""
        reservation = Reservation(reservation_code="RES-008")

        contact = reservation.add_contact(
            contact_type="EMERGENCY",
            full_name="Jane Smith",
            email="jane@example.com",
            phone="+0987654321",
        )

        assert contact.contact_type.value == "EMERGENCY"


class TestConfirmWithSupplier:
    """Test confirming reservation with supplier"""

    def test_confirm_from_pending_state(self) -> None:
        """Test confirming reservation from PENDING state"""
        reservation = Reservation(
            reservation_code="RES-009",
            status=ReservationStatus.PENDING,
        )
        reservation.supplier_name_snapshot = "LOCALIZA"

        # Add a contact for the event
        reservation.add_contact(
            contact_type="BOOKER",
            full_name="John Doe",
            email="john@example.com",
        )

        confirmed_at = datetime.utcnow()
        reservation.confirm_with_supplier(
            supplier_reservation_code="SUP-12345",
            supplier_confirmed_at=confirmed_at,
        )

        assert reservation.status == ReservationStatus.CONFIRMED
        assert reservation.supplier_reservation_code == "SUP-12345"
        assert reservation.supplier_confirmed_at == confirmed_at

    def test_confirm_generates_event(self) -> None:
        """Test confirming reservation generates ReservationConfirmed event"""
        reservation = Reservation(
            reservation_code="RES-010",
            status=ReservationStatus.PENDING,
            id=123,
        )
        reservation.supplier_name_snapshot = "LOCALIZA"
        reservation.add_contact(
            contact_type="BOOKER",
            full_name="John Doe",
            email="john@example.com",
        )

        reservation.confirm_with_supplier(
            supplier_reservation_code="SUP-67890",
            supplier_confirmed_at=datetime.utcnow(),
        )

        events = reservation.clear_events()

        assert len(events) == 1
        # Check it's a ReservationConfirmed event
        assert hasattr(events[0], "supplier_reservation_code")
        assert events[0].supplier_reservation_code == "SUP-67890"

    def test_confirm_from_invalid_state_raises_error(self) -> None:
        """Test confirming from invalid state raises error"""
        reservation = Reservation(
            reservation_code="RES-011",
            status=ReservationStatus.COMPLETED,  # Invalid state for confirmation
        )

        with pytest.raises(InvalidStateTransitionError):
            reservation.confirm_with_supplier(
                supplier_reservation_code="SUP-99999",
                supplier_confirmed_at=datetime.utcnow(),
            )


class TestMarkAsPaid:
    """Test marking reservation as paid"""

    def test_mark_as_paid(self) -> None:
        """Test marking reservation as paid"""
        reservation = Reservation(
            reservation_code="RES-012",
            payment_status=PaymentStatus.UNPAID,
        )

        reservation.mark_as_paid()

        assert reservation.payment_status == PaymentStatus.PAID

    def test_mark_as_paid_updates_timestamp(self) -> None:
        """Test marking as paid updates updated_at"""
        reservation = Reservation(
            reservation_code="RES-013",
            payment_status=PaymentStatus.UNPAID,
        )
        old_updated_at = reservation.updated_at

        # Wait a tiny bit to ensure timestamp changes
        import time
        time.sleep(0.01)

        reservation.mark_as_paid()

        assert reservation.updated_at > old_updated_at


class TestReservationProperties:
    """Test reservation properties"""

    def test_is_confirmed_property(self) -> None:
        """Test is_confirmed property"""
        reservation_pending = Reservation(
            reservation_code="RES-014",
            status=ReservationStatus.PENDING,
        )
        reservation_confirmed = Reservation(
            reservation_code="RES-015",
            status=ReservationStatus.CONFIRMED,
        )

        assert reservation_pending.is_confirmed is False
        assert reservation_confirmed.is_confirmed is True

    def test_is_paid_property(self) -> None:
        """Test is_paid property"""
        reservation_unpaid = Reservation(
            reservation_code="RES-016",
            payment_status=PaymentStatus.UNPAID,
        )
        reservation_paid = Reservation(
            reservation_code="RES-017",
            payment_status=PaymentStatus.PAID,
        )

        assert reservation_unpaid.is_paid is False
        assert reservation_paid.is_paid is True


class TestDomainEvents:
    """Test domain events management"""

    def test_clear_events_returns_and_clears(self) -> None:
        """Test clear_events returns events and clears internal list"""
        reservation = Reservation.create(
            reservation_code="RES-018",
            supplier_id=1,
            pickup_office_id=1,
            dropoff_office_id=1,
            car_category_id=1,
            supplier_car_product_id=1,
            pickup_datetime=datetime.utcnow(),
            dropoff_datetime=datetime.utcnow() + timedelta(days=1),
            rental_days=1,
            currency_code="USD",
            public_price_total=Decimal("100.00"),
            supplier_cost_total=Decimal("90.00"),
            status=ReservationStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
        )

        events_first = reservation.clear_events()
        events_second = reservation.clear_events()

        assert len(events_first) == 1
        assert len(events_second) == 0  # Already cleared
