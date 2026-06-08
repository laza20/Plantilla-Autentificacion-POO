from enum import Enum

class EstadoEntidad(str, Enum):
    ACTIVO = 'activo'
    ELIMINADO = 'eliminado'
    REPORTADO = 'reportado'
    SUSPENDIDO = 'suspendido'
    PENDIENTE = 'pendiente'