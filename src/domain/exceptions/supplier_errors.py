"""
Supplier Domain Exceptions
"""


class SupplierError(Exception):
    """Base exception for supplier errors"""
    pass


class SupplierConfirmationError(SupplierError):
    """Raised when supplier confirmation fails"""
    pass


class SupplierNotFoundError(SupplierError):
    """Raised when supplier is not found"""
    pass


class SupplierUnavailableError(SupplierError):
    """Raised when supplier service is unavailable"""
    pass


class SupplierTimeoutError(SupplierError):
    """Raised when supplier request times out"""
    pass
