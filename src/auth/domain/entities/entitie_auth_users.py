from dataclasses import dataclass
from datetime import date
from typing import Literal
from src.database.enums.estado_entidad import EstadoEntidad
from src.domain.exceptions.domain import LongitudExcedida


EMAIL_MAX_LENGTH = 255


@dataclass
class AuthUser:
    email: str
    password: str
    id_usuario: int | None = None
    imagen_url: str | None = None
    imagen_public_id: str | None = None
    estado: EstadoEntidad = EstadoEntidad.PENDIENTE
    created_at: date | None = None
    updated_at: date | None = None
    is_verified: bool = False
    eliminado_en: date | None = None

    def __post_init__(self) -> None:
        if len(self.email) > EMAIL_MAX_LENGTH:
            raise LongitudExcedida(f"email excede {EMAIL_MAX_LENGTH} caracteres")


@dataclass
class AuthUserNoTable:
    email: str
    password: str
    imagen_url: str | None = None
    imagen_public_id: str | None = None
    created_at: date | None = None
    updated_at: date | None = None
    is_verified: bool = False
    eliminado_en: date | None = None



@dataclass
class UsuarioCreado:
    id_usuario: int 
    email: str
    imagen_url: str | None = None
    created_at: date | None = None
    is_verified: bool = False


@dataclass
class UserRegisterDTO:
    email: str
    password: str


@dataclass
class UserModifyDTO:
    email: str | None = None


@dataclass
class AuthUserEmailValidation:
    email: str


@dataclass
class UserTokens:
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


@dataclass
class UsuarioLogeado:
    email: str
    imagen_url: str | None = None


@dataclass
class LoginResponse:
    tokens: UserTokens
    usuario: UsuarioLogeado


@dataclass
class AuthUserNoImage:
    email: str
    password: str