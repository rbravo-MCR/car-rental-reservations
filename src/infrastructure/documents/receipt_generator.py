"""
Receipt Generator Implementation
Genera recibos de pago en PDF usando WeasyPrint
"""
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from src.config.settings import get_settings
from src.domain.entities.payment import Payment
from src.domain.entities.reservation import Reservation

logger = structlog.get_logger()
settings = get_settings()

# Try to import WeasyPrint, but fallback gracefully if not available
try:
    from jinja2 import Environment, FileSystemLoader
    from weasyprint import HTML  # type: ignore[import-untyped]
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning("weasyprint_not_available", error=str(e))
    WEASYPRINT_AVAILABLE = False


class WeasyPrintReceiptGenerator:
    """
    Implementación de ReceiptGenerator usando WeasyPrint
    Genera PDFs profesionales a partir de templates HTML
    """

    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(str(settings.receipts_output_dir))

        if not WEASYPRINT_AVAILABLE:
            logger.warning("receipt_generator_initialized_without_weasyprint")
            self.jinja_env = None
            return

        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
        )

    async def generate(
        self,
        reservation: Reservation,
        payment: Payment,
        supplier_confirmation: str,
    ) -> str:
        """
        Generar recibo en PDF
        Args:
            reservation: Reserva
            payment: Pago
            supplier_confirmation: Código de confirmación del supplier
        Returns:
            str: URL del PDF generado
        """
        if not WEASYPRINT_AVAILABLE:
            logger.warning(
                "receipt_generation_skipped_weasyprint_unavailable",
                reservation_id=reservation.id,
            )
            return f"/receipts/mock_{reservation.reservation_code}.pdf"

        try:
            # Preparar datos para template
            context = self._prepare_context(
                reservation,
                payment,
                supplier_confirmation
            )

            # Renderizar HTML desde template
            template = self.jinja_env.get_template("receipt.html")
            html_content = template.render(**context)

            # Generar nombre de archivo
            filename = f"receipt_{reservation.reservation_code}.pdf"
            filepath = self.output_dir / filename

            # Generar PDF con WeasyPrint
            HTML(string=html_content).write_pdf(str(filepath))  # type: ignore[call-arg]

            logger.info(
                "receipt_generated",
                reservation_id=reservation.id,
                reservation_code=reservation.reservation_code,
                filepath=str(filepath),
            )

            # Retornar URL (en producción sería una URL de S3/CloudFront)
            # Por ahora retornamos path relativo
            return f"/receipts/{filename}"

        except Exception as e:
            logger.error(
                "receipt_generation_failed",
                reservation_id=reservation.id,
                error=str(e),
            )
            raise

    def _prepare_context(
        self,
        reservation: Reservation,
        payment: Payment,
        supplier_confirmation: str,
    ) -> dict[str, Any]:
        """Preparar contexto para el template"""

        # Obtener driver principal
        primary_driver = None
        for driver in reservation.drivers:
            if driver.is_primary_driver:
                primary_driver = driver
                break

        # Obtener contacto booker
        for contact in reservation.contacts:
            if contact.contact_type.value == 'BOOKER':
                break

        return {
            # Información de la empresa
            'company_name': 'Mexico Car Rental Platform',
            'company_address': 'Mérida, Yucatán, México',
            'company_email': 'soporte@mexicocarrental.com',
            'company_phone': '+52 999 123 4567',

            # Información del recibo
            'receipt_number': f"REC-{reservation.reservation_code}",
            'receipt_date': datetime.now(UTC).strftime('%Y-%m-%d'),
            'reservation_code': reservation.reservation_code,
            'supplier_confirmation': supplier_confirmation,

            # Cliente
            'customer_name': primary_driver.full_name if primary_driver else 'N/A',
            'customer_email': primary_driver.email if primary_driver else 'N/A',
            'customer_phone': primary_driver.phone if primary_driver else 'N/A',

            # Reserva
            'supplier_name': reservation.supplier_name_snapshot,
            'vehicle_category': reservation.car_category_name_snapshot,
            'acriss_code': reservation.car_acriss_code_snapshot,
            'pickup_location': reservation.pickup_office_name_snapshot,
            'pickup_datetime': reservation.pickup_datetime.strftime('%Y-%m-%d %H:%M'),
            'dropoff_location': reservation.dropoff_office_name_snapshot,
            'dropoff_datetime': reservation.dropoff_datetime.strftime('%Y-%m-%d %H:%M'),
            'rental_days': reservation.rental_days,

            # Pago
            'payment_method': payment.method or 'Credit Card',
            'payment_date': payment.captured_at.strftime('%Y-%m-%d %H:%M') if payment.captured_at else 'N/A',
            'payment_id': payment.stripe_payment_intent_id or 'N/A',
            'transaction_id': payment.stripe_charge_id or 'N/A',

            # Pricing
            'subtotal': float(reservation.public_price_total - reservation.taxes_total),
            'taxes': float(reservation.taxes_total),
            'fees': float(reservation.fees_total),
            'discount': float(reservation.discount_total),
            'total': float(reservation.public_price_total),
            'currency': reservation.currency_code,

            # Status
            'status': reservation.status.value,
            'payment_status': reservation.payment_status.value,
        }
