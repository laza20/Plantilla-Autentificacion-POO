from typing import Optional, Literal, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Date, Relationship
from datetime import date
from src.database.enums.estado_entidad import EstadoEntidad
from sqlalchemy import Column, text
from sqlalchemy.types import Enum as SAEnum

if TYPE_CHECKING:
    from src.auth.infrastructure.persistence.postgres.models.models_sesiones import Sesiones
    from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario
    from src.auth.infrastructure.persistence.postgres.models.models_recover_password import RecoverPassword
    from src.auth.infrastructure.persistence.postgres.models.models_history_password import HistoryPassword

class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password: str = Field(nullable=False)
    
    # Campos relacionados con la imagen del usuario
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    imagen_public_id: Optional[str] = Field(default=None, max_length=255)

    estado: Optional[EstadoEntidad] = Field(
        default=EstadoEntidad.PENDIENTE,
        sa_column=Column(
            SAEnum(
                EstadoEntidad,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                name="estado_entidad"
            ),
            server_default=text("'pendiente'::estado_entidad")
        )
    )

    created_at: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            server_default=text("CURRENT_DATE")
        )
    )
    updated_at: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            server_default=text("CURRENT_DATE")
        )
    )
    is_verified: bool = Field(default=False)

    usuario: Optional["Usuario"] = Relationship(
        back_populates="auth_user"
    )

    sesiones: list["Sesiones"] = Relationship(
        back_populates="usuario"
    )

    recover_password: list["RecoverPassword"] = Relationship(
        back_populates="usuario"
    )

    history_password: list["HistoryPassword"] = Relationship(
        back_populates="usuario"
    )


class AuthUserNoTable(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password: str = Field(nullable=False)
    # Campos relacionados con la imagen del usuario
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    imagen_public_id: Optional[str] = Field(default=None, max_length=255)

    created_at: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            server_default=text("CURRENT_DATE")
        )
    )
    updated_at: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            server_default=text("CURRENT_DATE")
        )
    )
    is_verified: bool = Field(default=False)


class UsuarioCreado(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False)
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            server_default=text("CURRENT_DATE")
        )
    )
    is_verified: bool = Field(default=False)


class UserRegisterDTO(SQLModel):
    email: str = Field(...)
    password: str = Field(nullable=False)

class UserTokens(SQLModel):
    access_token: str
    refresh_token: str
    token_type:  Literal["bearer"]  = Field(default="bearer")

class UsuarioLogeado(SQLModel):
    email     : str = Field(...)
    imagen_url       : Optional[str] = Field(None)

class LoginResponse(SQLModel):
    tokens: UserTokens
    usuario: UsuarioLogeado

class AuthUserNoImage(SQLModel):
    email: str = Field(max_length=55,nullable=False,unique=True)
    password: str = Field(nullable=False)

