"""
Unit tests for domain value objects
"""
import pytest

from src.domain.value_objects.reservation_status import PaymentStatus, ReservationStatus


class TestReservationStatus:
    """Test ReservationStatus value object"""

    def test_all_statuses_exist(self) -> None:
        """Test all expected statuses exist"""
        assert ReservationStatus.PENDING
        assert ReservationStatus.ON_REQUEST
        assert ReservationStatus.CONFIRMED
        assert ReservationStatus.IN_PROGRESS
        assert ReservationStatus.COMPLETED
        assert ReservationStatus.CANCELLED
        assert ReservationStatus.NO_SHOW
        assert ReservationStatus.FAILED

    def test_status_values(self) -> None:
        """Test status enum values"""
        assert ReservationStatus.PENDING.value == "pending"
        assert ReservationStatus.CONFIRMED.value == "confirmed"
        assert ReservationStatus.COMPLETED.value == "completed"
        assert ReservationStatus.CANCELLED.value == "cancelled"

    def test_status_comparison(self) -> None:
        """Test status comparison"""
        status1 = ReservationStatus.PENDING
        status2 = ReservationStatus.PENDING
        status3 = ReservationStatus.CONFIRMED

        assert status1 == status2
        assert status1 != status3

    def test_status_from_string(self) -> None:
        """Test creating status from string value"""
        status = ReservationStatus("confirmed")

        assert status == ReservationStatus.CONFIRMED

    def test_invalid_status_raises_error(self) -> None:
        """Test invalid status string raises ValueError"""
        with pytest.raises(ValueError):
            ReservationStatus("INVALID_STATUS")


class TestPaymentStatus:
    """Test PaymentStatus value object"""

    def test_all_payment_statuses_exist(self) -> None:
        """Test all expected payment statuses exist"""
        assert PaymentStatus.UNPAID
        assert PaymentStatus.PAID
        assert PaymentStatus.FAILED
        assert PaymentStatus.REFUNDED
        assert PaymentStatus.PARTIALLY_REFUNDED

    def test_payment_status_values(self) -> None:
        """Test payment status enum values"""
        assert PaymentStatus.UNPAID.value == "unpaid"
        assert PaymentStatus.PAID.value == "paid"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"
        assert PaymentStatus.PARTIALLY_REFUNDED.value == "partially_refunded"

    def test_payment_status_comparison(self) -> None:
        """Test payment status comparison"""
        status1 = PaymentStatus.UNPAID
        status2 = PaymentStatus.UNPAID
        status3 = PaymentStatus.PAID

        assert status1 == status2
        assert status1 != status3

    def test_payment_status_from_string(self) -> None:
        """Test creating payment status from string value"""
        status = PaymentStatus("paid")

        assert status == PaymentStatus.PAID

    def test_invalid_payment_status_raises_error(self) -> None:
        """Test invalid payment status string raises ValueError"""
        with pytest.raises(ValueError):
            PaymentStatus("INVALID_PAYMENT_STATUS")
