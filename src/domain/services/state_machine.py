"""
State Machine for Reservation Status
Define y valida transiciones de estado
"""
from domain.value_objects.reservation_status import ReservationStatus

# Matriz de transiciones permitidas
ALLOWED_TRANSITIONS: dict[ReservationStatus, list[ReservationStatus]] = {
    ReservationStatus.PENDING: [
        ReservationStatus.ON_REQUEST,
        ReservationStatus.CONFIRMED,
    ],
    ReservationStatus.ON_REQUEST: [
        ReservationStatus.CONFIRMED,
        ReservationStatus.PENDING,  # Retry
    ],
    ReservationStatus.CONFIRMED: [
        ReservationStatus.IN_PROGRESS,
        ReservationStatus.NO_SHOW,
    ],
    ReservationStatus.IN_PROGRESS: [
        ReservationStatus.COMPLETED,
    ],
    ReservationStatus.COMPLETED: [],  # Estado final
    ReservationStatus.NO_SHOW: [],     # Estado final
    ReservationStatus.CANCELLED: [],   # Estado final (manejado por otra app)
}


def can_transition(
    from_status: ReservationStatus,
    to_status: ReservationStatus
) -> bool:
    """
    Verifica si una transición de estado es válida

    Args:
        from_status: Estado actual
        to_status: Estado objetivo

    Returns:
        bool: True si la transición es válida

    Example:
        >>> can_transition(ReservationStatus.PENDING, ReservationStatus.CONFIRMED)
        True
        >>> can_transition(ReservationStatus.COMPLETED, ReservationStatus.PENDING)
        False
    """
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    return to_status in allowed


def get_allowed_transitions(
    from_status: ReservationStatus
) -> list[ReservationStatus]:
    """
    Obtiene lista de estados permitidos desde un estado dado

    Args:
        from_status: Estado actual

    Returns:
        list[ReservationStatus]: Lista de estados permitidos

    Example:
        >>> get_allowed_transitions(ReservationStatus.PENDING)
        [<ReservationStatus.ON_REQUEST: 'ON_REQUEST'>, <ReservationStatus.CONFIRMED: 'CONFIRMED'>]
    """
    return ALLOWED_TRANSITIONS.get(from_status, [])


def is_final_state(status: ReservationStatus) -> bool:
    """
    Verifica si un estado es final (no permite más transiciones)

    Args:
        status: Estado a verificar

    Returns:
        bool: True si es estado final

    Example:
        >>> is_final_state(ReservationStatus.COMPLETED)
        True
        >>> is_final_state(ReservationStatus.PENDING)
        False
    """
    return len(ALLOWED_TRANSITIONS.get(status, [])) == 0


def get_transition_description(
    from_status: ReservationStatus,
    to_status: ReservationStatus
) -> str:
    """
    Obtiene descripción legible de una transición

    Args:
        from_status: Estado origen
        to_status: Estado destino

    Returns:
        str: Descripción de la transición
    """
    transitions_map = {
        (ReservationStatus.PENDING, ReservationStatus.ON_REQUEST):
            "Enviando solicitud al proveedor",
        (ReservationStatus.PENDING, ReservationStatus.CONFIRMED):
            "Confirmación directa sin solicitud previa",
        (ReservationStatus.ON_REQUEST, ReservationStatus.CONFIRMED):
            "Proveedor confirmó la reserva",
        (ReservationStatus.ON_REQUEST, ReservationStatus.PENDING):
            "Reintento de solicitud al proveedor",
        (ReservationStatus.CONFIRMED, ReservationStatus.IN_PROGRESS):
            "Cliente retiró el vehículo (pickup)",
        (ReservationStatus.CONFIRMED, ReservationStatus.NO_SHOW):
            "Cliente no se presentó",
        (ReservationStatus.IN_PROGRESS, ReservationStatus.COMPLETED):
            "Cliente devolvió el vehículo (dropoff)",
    }

    return transitions_map.get(
        (from_status, to_status),
        f"Transición de {from_status.value} a {to_status.value}"
    )
