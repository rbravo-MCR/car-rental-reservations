"""
Pricing Calculator Domain Service
Calcula precios, márgenes, comisiones
"""
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal


class PricingCalculator:
    """
    Servicio de dominio para cálculos de precios
    """

    @staticmethod
    def calculate_rental_days(pickup_datetime: datetime, dropoff_datetime: datetime) -> int:
        """
        Calcula días de renta (redondeado hacia arriba)

        Args:
            pickup_datetime: Fecha/hora de recogida
            dropoff_datetime: Fecha/hora de devolución

        Returns:
            int: Número de días (mínimo 1)
        """
        delta = dropoff_datetime - pickup_datetime
        days = delta.days

        # Si hay horas adicionales, cuenta como un día más
        if delta.seconds > 0:
            days += 1

        # Mínimo 1 día
        return max(1, days)

    @staticmethod
    def calculate_public_price(
        supplier_cost: Decimal,
        markup_percentage: Decimal
    ) -> Decimal:
        """
        Calcula precio público aplicando markup

        Args:
            supplier_cost: Costo del proveedor
            markup_percentage: Porcentaje de markup (ej: 15.00 para 15%)

        Returns:
            Decimal: Precio público

        Example:
            >>> calculate_public_price(Decimal("100.00"), Decimal("15.00"))
            Decimal('115.00')
        """
        markup_multiplier = Decimal("1") + (markup_percentage / Decimal("100"))
        public_price = supplier_cost * markup_multiplier

        # Redondear a 2 decimales
        return public_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_commission(
        public_price: Decimal,
        supplier_cost: Decimal
    ) -> Decimal:
        """
        Calcula comisión (diferencia entre público y costo)

        Args:
            public_price: Precio público
            supplier_cost: Costo del proveedor

        Returns:
            Decimal: Comisión
        """
        commission = public_price - supplier_cost
        return max(Decimal("0"), commission)

    @staticmethod
    def apply_discount(
        original_price: Decimal,
        discount_type: str,
        discount_value: Decimal,
        max_discount: Decimal | None = None
    ) -> tuple[Decimal, Decimal]:
        """
        Aplica descuento y retorna nuevo precio y monto del descuento

        Args:
            original_price: Precio original
            discount_type: "PERCENT" o "FIXED_AMOUNT"
            discount_value: Valor del descuento (porcentaje o monto fijo)
            max_discount: Descuento máximo permitido (opcional)
        Returns:
            tuple: (precio_final, monto_descuento)
        Example:
            >>> apply_discount(Decimal("100.00"), "PERCENT", Decimal("10.00"))
            (Decimal('90.00'), Decimal('10.00'))
        """
        if discount_type == "PERCENT":
            discount_amount = original_price * \
                (discount_value / Decimal("100"))
        elif discount_type == "FIXED_AMOUNT":
            discount_amount = discount_value
        else:
            raise ValueError(f"Invalid discount type: {discount_type}")

        # Aplicar máximo si existe
        if max_discount and discount_amount > max_discount:
            discount_amount = max_discount

        # No puede ser mayor al precio original
        discount_amount = min(discount_amount, original_price)

        final_price = original_price - discount_amount

        return (
            final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            discount_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    @staticmethod
    def calculate_taxes(
        base_price: Decimal,
        tax_rate: Decimal
    ) -> Decimal:
        """
        Calcula impuestos

        Args:
            base_price: Precio base
            tax_rate: Tasa de impuesto (ej: 16.00 para 16%)
        Returns:
            Decimal: Monto de impuestos
        """
        taxes = base_price * (tax_rate / Decimal("100"))
        return taxes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_total_with_extras(
        base_price: Decimal,
        extras: list[tuple[Decimal, int]] | None = None
    ) -> Decimal:
        """
        Calcula total incluyendo extras

        Args:
            base_price: Precio base
            extras: Lista de tuplas (precio_unitario, cantidad)
        Returns:
            Decimal: Precio total
        Example:
            >>> calculate_total_with_extras(
            ...     Decimal("100.00"),
            ...     [(Decimal("10.00"), 2), (Decimal("5.00"), 1)]
            ... )
            Decimal('125.00')
        """
        total = base_price

        if extras:
            for unit_price, quantity in extras:
                total += unit_price * Decimal(str(quantity))

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
