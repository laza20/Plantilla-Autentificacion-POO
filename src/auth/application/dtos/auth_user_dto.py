from dataclasses import dataclass
from datetime import date
from typing import Literal
from src.auth.domain.entities.entitie_auth_users import UserTokens



@dataclass
class UsuarioCreado:
    id_usuario: int 
    email: str
    imagen_url: str | None = None
    created_at: date | None = None
    is_verified: bool = False



@dataclass
class UsuarioLogeado:
    email: str
    imagen_url: str | None = None


@dataclass
class LoginResponse:
    tokens: UserTokens
    usuario: UsuarioLogeado

@dataclass
class UserRegisterDTO:
    email: str
    password: str

@dataclass
class UserModifyDTO:
    email: str | None = None