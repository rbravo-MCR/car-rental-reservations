"""
Reservation Domain Exceptions
"""


class ReservationError(Exception):
    """Base exception for reservation errors"""
    pass


class ReservationCreationError(ReservationError):
    """Raised when reservation creation fails"""
    pass


class ReservationNotFoundError(ReservationError):
    """Raised when reservation is not found"""
    pass


class InvalidStateTransitionError(ReservationError):
    """Raised when attempting invalid state transition"""
    pass


class ReservationAlreadyExistsError(ReservationError):
    """Raised when reservation with same code already exists"""
    pass
