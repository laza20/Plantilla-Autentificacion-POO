from typing import Optional
from sqlmodel import SQLModel, Field, Date
from datetime import date
from src.database.enums import EstadoEntidad
from sqlalchemy import Column, text
from sqlalchemy.types import Enum as SAEnum

class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    
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