"""
Payment Domain Exceptions
"""


class PaymentError(Exception):
    """Base exception for payment errors"""
    pass


class PaymentFailedError(PaymentError):
    """Raised when payment processing fails"""
    pass


class PaymentGatewayError(PaymentError):
    """Raised when payment gateway is unavailable"""
    pass


class InvalidPaymentMethodError(PaymentError):
    """Raised when payment method is invalid"""
    pass
