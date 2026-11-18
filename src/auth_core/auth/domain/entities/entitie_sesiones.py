from dataclasses import dataclass
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
