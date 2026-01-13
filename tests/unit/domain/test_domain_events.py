"""
Unit tests for domain events
"""
from datetime import datetime

from src.domain.events.reservation_confirmed import ReservationConfirmed
from src.domain.events.reservation_created import ReservationCreated


class TestReservationCreatedEvent:
    """Test ReservationCreated domain event"""

    def test_create_event_with_all_fields(self) -> None:
        """Test creating event with all required fields"""
        pickup_datetime = datetime(2024, 1, 15, 10, 0, 0)
        occurred_at = datetime.utcnow()

        event = ReservationCreated(
            aggregate_id=123,
            reservation_code="RES-001",
            pickup_datetime=pickup_datetime,
            total_amount="299.99",
            currency_code="USD",
            occurred_at=occurred_at,
        )

        assert event.aggregate_id == 123
        assert event.reservation_code == "RES-001"
        assert event.pickup_datetime == pickup_datetime
        assert event.total_amount == "299.99"
        assert event.currency_code == "USD"
        assert event.occurred_at == occurred_at

    def test_create_event_with_default_timestamp(self) -> None:
        """Test creating event uses default timestamp if not provided"""
        pickup_datetime = datetime(2024, 1, 15, 10, 0, 0)

        event = ReservationCreated(
            aggregate_id=456,
            reservation_code="RES-002",
            pickup_datetime=pickup_datetime,
            total_amount="150.00",
            currency_code="EUR",
        )

        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)

    def test_event_has_required_fields(self) -> None:
        """Test event has all required fields for publishing"""
        pickup_datetime = datetime(2024, 1, 15, 10, 0, 0)

        event = ReservationCreated(
            aggregate_id=789,
            reservation_code="RES-003",
            pickup_datetime=pickup_datetime,
            total_amount="500.00",
            currency_code="MXN",
        )

        # Event should have all data needed for event store/message queue
        assert hasattr(event, "aggregate_id")
        assert hasattr(event, "reservation_code")
        assert hasattr(event, "occurred_at")
        assert event.aggregate_id == 789
        assert event.reservation_code == "RES-003"


class TestReservationConfirmedEvent:
    """Test ReservationConfirmed domain event"""

    def test_create_event_with_all_fields(self) -> None:
        """Test creating confirmed event with all fields"""
        occurred_at = datetime.utcnow()

        event = ReservationConfirmed(
            aggregate_id=123,
            reservation_code="RES-001",
            supplier_reservation_code="SUP-XYZ-789",
            supplier_name="LOCALIZA",
            customer_email="customer@example.com",
            occurred_at=occurred_at,
        )

        assert event.aggregate_id == 123
        assert event.reservation_code == "RES-001"
        assert event.supplier_reservation_code == "SUP-XYZ-789"
        assert event.supplier_name == "LOCALIZA"
        assert event.customer_email == "customer@example.com"
        assert event.occurred_at == occurred_at

    def test_create_event_with_default_timestamp(self) -> None:
        """Test creating confirmed event uses default timestamp"""
        event = ReservationConfirmed(
            aggregate_id=456,
            reservation_code="RES-002",
            supplier_reservation_code="SUP-ABC-123",
            supplier_name="Europcar",
            customer_email="user@example.com",
        )

        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)

    def test_event_has_required_fields(self) -> None:
        """Test event has all required fields"""
        event = ReservationConfirmed(
            aggregate_id=789,
            reservation_code="RES-003",
            supplier_reservation_code="SUP-DEF-456",
            supplier_name="Centauro",
            customer_email="test@example.com",
        )

        assert hasattr(event, "aggregate_id")
        assert hasattr(event, "supplier_reservation_code")
        assert hasattr(event, "occurred_at")

    def test_event_for_notification(self) -> None:
        """Test event contains data needed for customer notification"""
        event = ReservationConfirmed(
            aggregate_id=555,
            reservation_code="RES-NOTIFY",
            supplier_reservation_code="SUP-CONF-777",
            supplier_name="LOCALIZA",
            customer_email="notify@example.com",
        )

        # Event should have all data needed to send confirmation email
        assert event.customer_email  # Email recipient
        assert event.reservation_code  # For email subject/body
        assert event.supplier_reservation_code  # Confirmation number to share
        assert event.supplier_name  # Supplier info for customer
