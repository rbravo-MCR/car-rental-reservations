"""
Stripe Payment Gateway Implementation
Implementación concreta del gateway de pagos con Stripe
"""
import asyncio
from decimal import Decimal
from typing import Any

import stripe  # type: ignore[import-untyped]
import structlog

from src.application.ports.payment_gateway import PaymentGateway, PaymentResult
from src.config.settings import get_settings

logger = structlog.get_logger()


class StripePaymentGateway(PaymentGateway):
    """Implementación de PaymentGateway con Stripe"""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.stripe_secret_key
        self.webhook_secret = settings.stripe_webhook_secret
        # Configurar Stripe API key
        stripe.api_key = self.api_key

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
            # Stripe SDK es síncrono, ejecutar en thread separado
            payment_intent = await asyncio.to_thread(
                stripe.PaymentIntent.create,
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
                if hasattr(payment_intent, 'charges'):
                    charges = getattr(payment_intent, 'charges', None)
                    if charges:
                        charges_data = getattr(charges, 'data', None)
                        if charges_data and len(charges_data) > 0:
                            charge_id = getattr(charges_data[0], 'id', None)

                # Obtener método de pago
                payment_method = None
                if payment_intent.payment_method:
                    # payment_method puede ser un ID (str) o un objeto expandido
                    pm_id = payment_intent.payment_method
                    if isinstance(pm_id, str):
                        pm = await asyncio.to_thread(
                            stripe.PaymentMethod.retrieve,
                            pm_id
                        )
                        payment_method = getattr(pm, 'type', None)  # 'card', 'bank_transfer', etc
                    else:
                        # Ya es un objeto expandido
                        payment_method = getattr(pm_id, 'type', None)

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

        except stripe.error.CardError as e:  # type: ignore[attr-defined]
            # Tarjeta rechazada
            logger.error(
                "stripe_card_error",
                error_code=getattr(e, 'code', None),  # type: ignore[arg-type]
                error_message=str(e),  # type: ignore[arg-type]
            )

            user_msg = getattr(e, 'user_message', str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Card error: {user_msg}",
            )

        except stripe.error.RateLimitError as e:  # type: ignore[attr-defined]
            logger.error("stripe_rate_limit", error=str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Rate limit exceeded. Please try again later.",
            )

        except stripe.error.InvalidRequestError as e:  # type: ignore[attr-defined]
            logger.error("stripe_invalid_request", error=str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Invalid request: {str(e)}",  # type: ignore[arg-type]
            )

        except stripe.error.AuthenticationError as e:  # type: ignore[attr-defined]
            logger.error("stripe_authentication_error", error=str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Authentication with Stripe failed.",
            )

        except stripe.error.APIConnectionError as e:  # type: ignore[attr-defined]
            logger.error("stripe_connection_error", error=str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message="Network error. Please try again.",
            )

        except stripe.error.StripeError as e:  # type: ignore[attr-defined]
            logger.error("stripe_general_error", error=str(e))  # type: ignore[arg-type]
            return PaymentResult(
                success=False,
                payment_intent_id="",
                amount=amount,
                currency_code=currency,
                status='failed',
                error_message=f"Payment error: {str(e)}",  # type: ignore[arg-type]
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
            # Stripe webhook verification es síncrono, ejecutar en thread
            event = await asyncio.to_thread(
                stripe.Webhook.construct_event,  # type: ignore[arg-type]
                payload,
                signature,
                secret,
            )

            logger.info(
                "stripe_webhook_verified",
                event_type=getattr(event, 'type', None),
                event_id=getattr(event, 'id', None),
            )

            return event

        except ValueError as e:
            logger.error("stripe_webhook_invalid_payload", error=str(e))
            raise

        except stripe.error.SignatureVerificationError as e:  # type: ignore[attr-defined]
            logger.error("stripe_webhook_invalid_signature", error=str(e))  # type: ignore[arg-type]
            raise ValueError("Invalid webhook signature") from e
