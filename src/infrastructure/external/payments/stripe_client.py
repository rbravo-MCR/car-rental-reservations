"""
Stripe Payment Gateway Implementation
Implementación concreta del gateway de pagos con Stripe
"""
from decimal import Decimal
from typing import Any

import stripe
import structlog
from src.config.settings import get_settings

from src.application.ports.payment_gateway import PaymentGateway, PaymentResult

logger = structlog.get_logger()
settings = get_settings()

# Configurar Stripe API key
stripe.api_key = settings.stripe_secret_key


class StripePaymentGateway(PaymentGateway):
    """Implementación de PaymentGateway con Stripe"""

    def __init__(self):
        self.api_key = settings.stripe_secret_key
        self.webhook_secret = settings.stripe_webhook_secret

    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_method_id: str,
        description: str,
        metadata: dict[str, str] | None = None,
    ) -> PaymentResult:
        """
        Procesar cargo inmediato con Stripe
        Flujo:
        1. Crear Payment Intent
        2. Confirmar automáticamente
        3. Retornar resultado
        """
        try:
            # Convertir a centavos (Stripe requiere integers)
            amount_cents = int(amount * 100)

            logger.info(
                "stripe_charge_started",
                amount=float(amount),
                currency=currency,
                payment_method_id=payment_method_id,
            )

            # Crear y confirmar Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                payment_method=payment_method_id,
                description=description,
                metadata=metadata or {},
                confirm=True,  # Confirmar inmediatamente
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never',  # No redirects
                },
            )

            logger.info(
                "stripe_payment_intent_created",
                payment_intent_id=payment_intent.id,
                status=payment_intent.status,
            )

            # Verificar si fue exitoso
            if payment_intent.status == 'succeeded':
                # Obtener charge ID
                charge_id = None
                if payment_intent.charges and payment_intent.charges.data:
                    charge_id = payment_intent.charges.data[0].id

                # Obtener método de pago
                payment_method = None
                if payment_intent.payment_method:
                    pm = stripe.PaymentMethod.retrieve(
                        payment_intent.payment_method)
                    payment_method = pm.type  # 'card', 'bank_transfer', etc

                return PaymentResult(
                    success=True,
                    payment_intent_id=payment_intent.id,
                    charge_id=charge_id,
                    amount=amount,
                    currency_code=currency,
                    status='succeeded',
                    method=payment_method,
                )

            else:
                # Pago no exitoso
                logger.warning(
                    "stripe_payment_not_succeeded",
                    payment_intent_id=payment_intent.id,
                    status=payment_intent.status,
                )

                return PaymentResult(
                    success=False,
                    payment_intent_id=payment_intent.id,
                    amount=amount,
                    currency_code=currency,
                    status=payment_intent.status,
                    error_message=f"Payment status: {payment_intent.status}",
                )

        except stripe.error.CardError as e:
            # Tarjeta rechazada
            logger.error(
                "stripe_card_error",
                error_code=e.code,
                error_message=str(e),
            )

            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Card error: {e.user_message}",
            )

        except stripe.error.RateLimitError as e:
            logger.error("stripe_rate_limit", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Rate limit exceeded. Please try again later.",
            )

        except stripe.error.InvalidRequestError as e:
            logger.error("stripe_invalid_request", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Invalid request: {str(e)}",
            )

        except stripe.error.AuthenticationError as e:
            logger.error("stripe_authentication_error", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Authentication with Stripe failed.",
            )

        except stripe.error.APIConnectionError as e:
            logger.error("stripe_connection_error", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Network error. Please try again.",
            )

        except stripe.error.StripeError as e:
            logger.error("stripe_general_error", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Payment error: {str(e)}",
            )

        except Exception as e:
            logger.error("stripe_unexpected_error", error=str(e))
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="An unexpected error occurred.",
            )

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> dict[str, Any]:
        """
        Verificar firma de webhook de Stripe
        Args:
            payload: Body del request (bytes)
            signature: Header 'Stripe-Signature'
            secret: Webhook secret de Stripe
        Returns:
            Event parseado si la firma es válida
        Raises:
            ValueError: Si la firma es inválida
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=secret,
            )

            logger.info(
                "stripe_webhook_verified",
                event_type=event.type,
                event_id=event.id,
            )

            return event

        except ValueError as e:
            logger.error("stripe_webhook_invalid_payload", error=str(e))
            raise

        except stripe.error.SignatureVerificationError as e:
            logger.error("stripe_webhook_invalid_signature", error=str(e))
            raise ValueError("Invalid webhook signature") from e
