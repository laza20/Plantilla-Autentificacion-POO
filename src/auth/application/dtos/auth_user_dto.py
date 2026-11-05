from dataclasses import dataclass
from datetime import date
from typing import Literal



@dataclass
class UsuarioCreado:
    id_usuario: int 
    email: str
    imagen_url: str | None = None
    created_at: date | None = None
    is_verified: bool = False
