from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Sesion:
    id_sesion: int
    hash_refresh_token: str
    id_usuario: int
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    inicio_sesion: Optional[datetime] = None


@dataclass(frozen=True)
class SesionVisual:
    """Sesión para mostrar al usuario: sin hash_refresh_token."""
    id_sesion: int
    id_usuario: int
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    inicio_sesion: Optional[datetime] = None
    es_actual: bool = False


@dataclass(frozen=True)
class ListaSesiones:
    sesiones: list[SesionVisual] = field(default_factory=list)