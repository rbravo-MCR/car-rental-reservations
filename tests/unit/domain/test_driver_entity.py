"""
Unit tests for Driver entity
"""
from datetime import date

import pytest

from src.domain.entities.driver import Driver


class TestDriverCreation:
    """Test Driver entity creation"""

    def test_create_minimal_driver(self) -> None:
        """Test creating driver with minimal required fields"""
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
        )

        assert driver.first_name == "John"
        assert driver.last_name == "Doe"
        assert driver.email == "john@example.com"
        assert driver.phone == "+1234567890"
        assert driver.is_primary_driver is True  # Default value

    def test_create_complete_driver(self) -> None:
        """Test creating driver with all fields"""
        birth_date = date(1990, 5, 15)
        driver = Driver(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+0987654321",
            is_primary_driver=False,
            date_of_birth=birth_date,
            driver_license_number="DL123456",
            driver_license_country="US",
        )

        assert driver.first_name == "Jane"
        assert driver.is_primary_driver is False
        assert driver.date_of_birth == birth_date
        assert driver.driver_license_number == "DL123456"
        assert driver.driver_license_country == "US"

    def test_create_driver_without_name_raises_error(self) -> None:
        """Test creating driver without name raises ValueError"""
        with pytest.raises(ValueError, match="must have first and last name"):
            Driver(
                first_name="",
                last_name="Doe",
                email="test@example.com",
            )

        with pytest.raises(ValueError, match="must have first and last name"):
            Driver(
                first_name="John",
                last_name="",
                email="test@example.com",
            )


class TestDriverFullName:
    """Test Driver full_name property"""

    def test_full_name(self) -> None:
        """Test full_name property combines first and last name"""
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
        )

        assert driver.full_name == "John Doe"

    def test_full_name_with_spaces(self) -> None:
        """Test full_name handles names with spaces"""
        driver = Driver(
            first_name="Mary Jane",
            last_name="Watson",
            email="mary@example.com",
            phone="+1234567890",
        )

        assert driver.full_name == "Mary Jane Watson"


class TestIsValidForRental:
    """Test driver rental validity"""

    def test_valid_driver_over_21_with_license(self) -> None:
        """Test driver over 21 with license is valid for rental"""
        birth_date = date.today().replace(year=date.today().year - 25)
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            date_of_birth=birth_date,
            driver_license_number="DL123456",
        )

        assert driver.is_valid_for_rental() is True

    def test_driver_exactly_21_with_license_is_valid(self) -> None:
        """Test driver exactly 21 years old with license is valid"""
        birth_date = date.today().replace(year=date.today().year - 21)
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            date_of_birth=birth_date,
            driver_license_number="DL123456",
        )

        assert driver.is_valid_for_rental() is True

    def test_driver_under_21_is_invalid(self) -> None:
        """Test driver under 21 is invalid for rental"""
        birth_date = date.today().replace(year=date.today().year - 20)
        driver = Driver(
            first_name="Young",
            last_name="Driver",
            email="young@example.com",
            phone="+1234567890",
            date_of_birth=birth_date,
            driver_license_number="DL789012",
        )

        assert driver.is_valid_for_rental() is False

    def test_driver_without_license_is_invalid(self) -> None:
        """Test driver without license number is invalid"""
        birth_date = date.today().replace(year=date.today().year - 30)
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            date_of_birth=birth_date,
        )

        assert driver.is_valid_for_rental() is False

    def test_driver_without_dob_but_with_license_is_valid(self) -> None:
        """Test driver without DOB but with license is valid (manual verification)"""
        driver = Driver(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            driver_license_number="DL999888",
        )

        # Without DOB, age check is skipped but license is required
        assert driver.is_valid_for_rental() is True
