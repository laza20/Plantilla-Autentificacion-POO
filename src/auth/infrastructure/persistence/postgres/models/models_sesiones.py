from typing import Optional,  TYPE_CHECKING
from sqlmodel import SQLModel, Field, DateTime, Relationship
from datetime import datetime
from sqlalchemy import Column, text

if TYPE_CHECKING:
    from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser

class Sesiones(SQLModel, table=True):
    __tablename__ = "sesiones"

    id_sesion: Optional[int] = Field(default=None, primary_key=True)
    
    hash_refresh_token: str = Field(unique=True, index=True, nullable=False, max_length=64)
    user_agent: str = Field(default=None, max_length=254)
    ip: str = Field(default=None, max_length=254)
    inicio_sesion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)


    usuario: Optional["AuthUser"] = Relationship(
        back_populates="sesiones"
    )


class SesionesNoTable(SQLModel):
    id_sesion: Optional[int] = Field(default=None, primary_key=True)
    hash_refresh_token: str = Field(unique=True, index=True, nullable=False, max_length=64)
    user_agent: str = Field(default=None, max_length=254)
    ip: str = Field(default=None, max_length=254)
    inicio_sesion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime ,server_default=text("CURRENT_TIMESTAMP")))
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)


class SesionesVisual(SQLModel):
    id_sesion: Optional[int] = Field(default=None, primary_key=True)
    user_agent: str = Field(default=None, max_length=254)
    ip: str = Field(default=None, max_length=254)
    inicio_sesion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime ,server_default=text("CURRENT_TIMESTAMP")))
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)
    es_actual: Optional[bool] = Field(default=False)

class ListaSesiones(SQLModel):
    sesiones: list[SesionesVisual]