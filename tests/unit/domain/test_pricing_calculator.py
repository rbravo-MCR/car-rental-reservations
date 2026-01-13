"""
Unit tests for PricingCalculator domain service
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.domain.services.pricing_calculator import PricingCalculator


class TestCalculateRentalDays:
    """Test rental days calculation"""

    def test_same_day_rental(self) -> None:
        """Test same day rental returns 1 day"""
        pickup = datetime(2024, 1, 1, 10, 0, 0)
        dropoff = datetime(2024, 1, 1, 18, 0, 0)

        days = PricingCalculator.calculate_rental_days(pickup, dropoff)

        assert days == 1

    def test_exact_24_hours(self) -> None:
        """Test exactly 24 hours returns 1 day"""
        pickup = datetime(2024, 1, 1, 10, 0, 0)
        dropoff = datetime(2024, 1, 2, 10, 0, 0)

        days = PricingCalculator.calculate_rental_days(pickup, dropoff)

        assert days == 1

    def test_24_hours_plus_one_minute(self) -> None:
        """Test 24 hours + 1 minute returns 2 days"""
        pickup = datetime(2024, 1, 1, 10, 0, 0)
        dropoff = datetime(2024, 1, 2, 10, 1, 0)

        days = PricingCalculator.calculate_rental_days(pickup, dropoff)

        assert days == 2

    def test_multiple_days(self) -> None:
        """Test multiple complete days"""
        pickup = datetime(2024, 1, 1, 10, 0, 0)
        dropoff = datetime(2024, 1, 5, 10, 0, 0)

        days = PricingCalculator.calculate_rental_days(pickup, dropoff)

        assert days == 4

    def test_week_rental(self) -> None:
        """Test one week rental"""
        pickup = datetime(2024, 1, 1, 10, 0, 0)
        dropoff = datetime(2024, 1, 8, 10, 0, 0)

        days = PricingCalculator.calculate_rental_days(pickup, dropoff)

        assert days == 7


class TestCalculatePublicPrice:
    """Test public price calculation with markup"""

    def test_15_percent_markup(self) -> None:
        """Test 15% markup calculation"""
        supplier_cost = Decimal("100.00")
        markup = Decimal("15.00")

        public_price = PricingCalculator.calculate_public_price(supplier_cost, markup)

        assert public_price == Decimal("115.00")

    def test_20_percent_markup(self) -> None:
        """Test 20% markup calculation"""
        supplier_cost = Decimal("250.00")
        markup = Decimal("20.00")

        public_price = PricingCalculator.calculate_public_price(supplier_cost, markup)

        assert public_price == Decimal("300.00")

    def test_markup_with_rounding(self) -> None:
        """Test markup with rounding to 2 decimals"""
        supplier_cost = Decimal("123.45")
        markup = Decimal("12.50")

        public_price = PricingCalculator.calculate_public_price(supplier_cost, markup)

        assert public_price == Decimal("138.88")

    def test_zero_markup(self) -> None:
        """Test zero markup returns same price"""
        supplier_cost = Decimal("100.00")
        markup = Decimal("0.00")

        public_price = PricingCalculator.calculate_public_price(supplier_cost, markup)

        assert public_price == supplier_cost


class TestCalculateCommission:
    """Test commission calculation"""

    def test_positive_commission(self) -> None:
        """Test positive commission calculation"""
        public_price = Decimal("115.00")
        supplier_cost = Decimal("100.00")

        commission = PricingCalculator.calculate_commission(public_price, supplier_cost)

        assert commission == Decimal("15.00")

    def test_zero_commission(self) -> None:
        """Test zero commission when prices are equal"""
        public_price = Decimal("100.00")
        supplier_cost = Decimal("100.00")

        commission = PricingCalculator.calculate_commission(public_price, supplier_cost)

        assert commission == Decimal("0")

    def test_negative_commission_returns_zero(self) -> None:
        """Test negative commission returns zero"""
        public_price = Decimal("90.00")
        supplier_cost = Decimal("100.00")

        commission = PricingCalculator.calculate_commission(public_price, supplier_cost)

        assert commission == Decimal("0")


class TestApplyDiscount:
    """Test discount application"""

    def test_percent_discount(self) -> None:
        """Test percentage discount"""
        original_price = Decimal("100.00")

        final_price, discount_amount = PricingCalculator.apply_discount(
            original_price, "PERCENT", Decimal("10.00")
        )

        assert final_price == Decimal("90.00")
        assert discount_amount == Decimal("10.00")

    def test_fixed_amount_discount(self) -> None:
        """Test fixed amount discount"""
        original_price = Decimal("100.00")

        final_price, discount_amount = PricingCalculator.apply_discount(
            original_price, "FIXED_AMOUNT", Decimal("25.00")
        )

        assert final_price == Decimal("75.00")
        assert discount_amount == Decimal("25.00")

    def test_discount_with_max_limit(self) -> None:
        """Test discount is capped at max limit"""
        original_price = Decimal("200.00")
        max_discount = Decimal("15.00")

        final_price, discount_amount = PricingCalculator.apply_discount(
            original_price, "PERCENT", Decimal("20.00"), max_discount
        )

        # 20% of 200 = 40, but capped at 15
        assert discount_amount == Decimal("15.00")
        assert final_price == Decimal("185.00")

    def test_discount_cannot_exceed_price(self) -> None:
        """Test discount cannot be greater than original price"""
        original_price = Decimal("50.00")

        final_price, discount_amount = PricingCalculator.apply_discount(
            original_price, "FIXED_AMOUNT", Decimal("100.00")
        )

        assert discount_amount == Decimal("50.00")
        assert final_price == Decimal("0.00")

    def test_invalid_discount_type_raises_error(self) -> None:
        """Test invalid discount type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid discount type"):
            PricingCalculator.apply_discount(
                Decimal("100.00"), "INVALID", Decimal("10.00")
            )


class TestCalculateTaxes:
    """Test tax calculation"""

    def test_16_percent_tax(self) -> None:
        """Test 16% tax calculation (Mexico IVA)"""
        base_price = Decimal("100.00")
        tax_rate = Decimal("16.00")

        taxes = PricingCalculator.calculate_taxes(base_price, tax_rate)

        assert taxes == Decimal("16.00")

    def test_tax_with_rounding(self) -> None:
        """Test tax calculation with rounding"""
        base_price = Decimal("123.45")
        tax_rate = Decimal("16.00")

        taxes = PricingCalculator.calculate_taxes(base_price, tax_rate)

        assert taxes == Decimal("19.75")

    def test_zero_tax(self) -> None:
        """Test zero tax rate"""
        base_price = Decimal("100.00")
        tax_rate = Decimal("0.00")

        taxes = PricingCalculator.calculate_taxes(base_price, tax_rate)

        assert taxes == Decimal("0.00")


class TestCalculateTotalWithExtras:
    """Test total calculation with extras"""

    def test_no_extras(self) -> None:
        """Test total without extras"""
        base_price = Decimal("100.00")

        total = PricingCalculator.calculate_total_with_extras(base_price)

        assert total == Decimal("100.00")

    def test_single_extra(self) -> None:
        """Test total with single extra"""
        base_price = Decimal("100.00")
        extras = [(Decimal("10.00"), 1)]

        total = PricingCalculator.calculate_total_with_extras(base_price, extras)

        assert total == Decimal("110.00")

    def test_multiple_extras(self) -> None:
        """Test total with multiple extras"""
        base_price = Decimal("100.00")
        extras = [
            (Decimal("10.00"), 2),  # GPS x2
            (Decimal("5.00"), 1),   # Baby seat x1
        ]

        total = PricingCalculator.calculate_total_with_extras(base_price, extras)

        assert total == Decimal("125.00")

    def test_extras_with_zero_quantity(self) -> None:
        """Test extras with zero quantity"""
        base_price = Decimal("100.00")
        extras = [(Decimal("10.00"), 0)]

        total = PricingCalculator.calculate_total_with_extras(base_price, extras)

        assert total == Decimal("100.00")
