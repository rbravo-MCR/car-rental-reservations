"""
Unit tests for Payment entity
"""
from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.entities.payment import Payment
from src.domain.value_objects.reservation_status import PaymentStatus


class TestPaymentCreation:
    """Test Payment entity creation"""

    def test_create_minimal_payment(self) -> None:
        """Test creating payment with minimal required fields"""
        payment = Payment.create(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123456",
            amount=Decimal("299.99"),
            currency_code="USD",
            status=PaymentStatus.PAID,
        )

        assert payment.reservation_id == 1
        assert payment.provider == "STRIPE"
        assert payment.provider_transaction_id == "ch_123456"
        assert payment.amount == Decimal("299.99")
        assert payment.currency_code == "USD"
        assert payment.status == PaymentStatus.PAID
        assert payment.created_at is not None

    def test_create_payment_with_stripe_fields(self) -> None:
        """Test creating payment with Stripe-specific fields"""
        payment = Payment.create(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_789012",
            stripe_payment_intent_id="pi_123456789",
            amount=Decimal("150.00"),
            currency_code="EUR",
            status=PaymentStatus.PAID,
            method="card",
        )

        assert payment.stripe_payment_intent_id == "pi_123456789"
        assert payment.method == "card"

    def test_create_payment_with_all_fields(self) -> None:
        """Test creating payment with all optional fields"""
        payment = Payment.create(
            reservation_id=3,
            provider="STRIPE",
            provider_transaction_id="ch_345678",
            stripe_payment_intent_id="pi_987654321",
            stripe_charge_id="ch_345678",
            stripe_event_id="evt_123",
            amount=Decimal("500.00"),
            currency_code="MXN",
            status=PaymentStatus.PAID,
            method="card",
            fee_amount=Decimal("15.50"),
            net_amount=Decimal("484.50"),
        )

        assert payment.stripe_charge_id == "ch_345678"
        assert payment.stripe_event_id == "evt_123"
        assert payment.fee_amount == Decimal("15.50")
        assert payment.net_amount == Decimal("484.50")

    def test_create_payment_initializes_defaults(self) -> None:
        """Test create method initializes default values"""
        payment = Payment.create(
            reservation_id=4,
            provider="STRIPE",
            provider_transaction_id="ch_111222",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PENDING,
        )

        assert payment.amount_refunded == Decimal("0")
        assert payment.captured_at is None
        assert payment.refunded_at is None
        assert payment.fee_amount is None
        assert payment.net_amount is None


class TestMarkAsCaptured:
    """Test marking payment as captured"""

    def test_mark_as_captured_updates_status(self) -> None:
        """Test mark_as_captured updates status to PAID"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PENDING,
        )

        payment.mark_as_captured("ch_123456")

        assert payment.status == PaymentStatus.PAID
        assert payment.stripe_charge_id == "ch_123456"
        assert payment.captured_at is not None

    def test_mark_as_captured_sets_timestamp(self) -> None:
        """Test mark_as_captured sets captured_at timestamp"""
        payment = Payment(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_456",
            amount=Decimal("200.00"),
            currency_code="EUR",
            status=PaymentStatus.PENDING,
        )

        before = datetime.utcnow()
        payment.mark_as_captured("ch_789012")
        after = datetime.utcnow()

        assert payment.captured_at is not None
        assert before <= payment.captured_at <= after

    def test_mark_as_captured_updates_updated_at(self) -> None:
        """Test mark_as_captured updates updated_at timestamp"""
        payment = Payment(
            reservation_id=3,
            provider="STRIPE",
            provider_transaction_id="ch_789",
            amount=Decimal("300.00"),
            currency_code="MXN",
            status=PaymentStatus.PENDING,
        )
        old_updated_at = payment.updated_at

        import time
        time.sleep(0.01)

        payment.mark_as_captured("ch_345678")

        assert payment.updated_at > old_updated_at


class TestMarkAsRefunded:
    """Test marking payment as refunded"""

    def test_mark_as_refunded_full(self) -> None:
        """Test full refund updates status and amount"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PAID,
            amount_refunded=Decimal("0"),
        )

        payment.mark_as_refunded(Decimal("100.00"))

        assert payment.status == PaymentStatus.REFUNDED
        assert payment.amount_refunded == Decimal("100.00")
        assert payment.refunded_at is not None

    def test_mark_as_refunded_partial(self) -> None:
        """Test partial refund updates status correctly"""
        payment = Payment(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_456",
            amount=Decimal("200.00"),
            currency_code="EUR",
            status=PaymentStatus.PAID,
            amount_refunded=Decimal("0"),
        )

        payment.mark_as_refunded(Decimal("50.00"))

        assert payment.status == PaymentStatus.PARTIALLY_REFUNDED
        assert payment.amount_refunded == Decimal("50.00")
        assert payment.refunded_at is not None

    def test_mark_as_refunded_sets_timestamp(self) -> None:
        """Test mark_as_refunded sets refunded_at timestamp"""
        payment = Payment(
            reservation_id=3,
            provider="STRIPE",
            provider_transaction_id="ch_789",
            amount=Decimal("300.00"),
            currency_code="MXN",
            status=PaymentStatus.PAID,
            amount_refunded=Decimal("0"),
        )

        before = datetime.utcnow()
        payment.mark_as_refunded(Decimal("100.00"))
        after = datetime.utcnow()

        assert payment.refunded_at is not None
        assert before <= payment.refunded_at <= after

    def test_mark_as_refunded_updates_updated_at(self) -> None:
        """Test mark_as_refunded updates updated_at timestamp"""
        payment = Payment(
            reservation_id=4,
            provider="STRIPE",
            provider_transaction_id="ch_999",
            amount=Decimal("150.00"),
            currency_code="USD",
            status=PaymentStatus.PAID,
            amount_refunded=Decimal("0"),
        )
        old_updated_at = payment.updated_at

        import time
        time.sleep(0.01)

        payment.mark_as_refunded(Decimal("150.00"))

        assert payment.updated_at > old_updated_at


class TestPaymentProperties:
    """Test payment computed properties"""

    def test_is_captured_property(self) -> None:
        """Test is_captured property"""
        payment_captured = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PAID,
        )
        payment_pending = Payment(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_456",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PENDING,
        )

        assert payment_captured.is_captured is True
        assert payment_pending.is_captured is False

    def test_is_refunded_property_full_refund(self) -> None:
        """Test is_refunded property with full refund"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.REFUNDED,
            amount_refunded=Decimal("100.00"),
        )

        assert payment.is_refunded is True

    def test_is_refunded_property_partial_refund(self) -> None:
        """Test is_refunded property with partial refund"""
        payment = Payment(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_456",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PARTIALLY_REFUNDED,
            amount_refunded=Decimal("50.00"),
        )

        assert payment.is_refunded is True

    def test_is_refunded_property_no_refund(self) -> None:
        """Test is_refunded property without refund"""
        payment = Payment(
            reservation_id=3,
            provider="STRIPE",
            provider_transaction_id="ch_789",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PAID,
            amount_refunded=Decimal("0"),
        )

        assert payment.is_refunded is False

    def test_is_failed_property(self) -> None:
        """Test is_failed property"""
        payment_failed = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.FAILED,
        )
        payment_paid = Payment(
            reservation_id=2,
            provider="STRIPE",
            provider_transaction_id="ch_456",
            amount=Decimal("100.00"),
            currency_code="USD",
            status=PaymentStatus.PAID,
        )

        assert payment_failed.is_failed is True
        assert payment_paid.is_failed is False


class TestDecimalConversion:
    """Test Decimal conversion in __post_init__"""

    def test_decimal_conversion_from_float(self) -> None:
        """Test that __post_init__ converts float to Decimal"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=99.99,  # Pass as float
            currency_code="USD",
            amount_refunded=5.50,  # Pass as float
        )

        assert isinstance(payment.amount, Decimal)
        assert isinstance(payment.amount_refunded, Decimal)
        assert payment.amount == Decimal("99.99")
        assert payment.amount_refunded == Decimal("5.50")

    def test_decimal_conversion_optional_fields(self) -> None:
        """Test Decimal conversion for optional fields"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            fee_amount=3.50,  # Pass as float
            net_amount=96.50,  # Pass as float
        )

        assert isinstance(payment.fee_amount, Decimal)
        assert isinstance(payment.net_amount, Decimal)
        assert payment.fee_amount == Decimal("3.50")
        assert payment.net_amount == Decimal("96.50")


class TestStripeSpecificFields:
    """Test Stripe-specific field handling"""

    def test_stripe_payment_intent_id(self) -> None:
        """Test Stripe payment intent ID is stored"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            stripe_payment_intent_id="pi_abc123",
            amount=Decimal("100.00"),
            currency_code="USD",
        )

        assert payment.stripe_payment_intent_id == "pi_abc123"

    def test_stripe_charge_id(self) -> None:
        """Test Stripe charge ID is stored"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            stripe_charge_id="ch_xyz789",
            amount=Decimal("100.00"),
            currency_code="USD",
        )

        assert payment.stripe_charge_id == "ch_xyz789"

    def test_stripe_event_id(self) -> None:
        """Test Stripe event ID is stored"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            stripe_event_id="evt_def456",
            amount=Decimal("100.00"),
            currency_code="USD",
        )

        assert payment.stripe_event_id == "evt_def456"

    def test_stripe_fees_and_net_amount(self) -> None:
        """Test Stripe fees and net amount calculation"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            fee_amount=Decimal("2.90"),  # Stripe fee: 2.9% + $0.30
            net_amount=Decimal("97.10"),
        )

        assert payment.fee_amount == Decimal("2.90")
        assert payment.net_amount == Decimal("97.10")
        # Verify calculation
        assert payment.amount - payment.fee_amount == payment.net_amount


class TestPaymentMethod:
    """Test payment method tracking"""

    def test_payment_method_card(self) -> None:
        """Test card payment method"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
            method="card",
        )

        assert payment.method == "card"

    def test_payment_method_optional(self) -> None:
        """Test payment method is optional"""
        payment = Payment(
            reservation_id=1,
            provider="STRIPE",
            provider_transaction_id="ch_123",
            amount=Decimal("100.00"),
            currency_code="USD",
        )

        assert payment.method is None
