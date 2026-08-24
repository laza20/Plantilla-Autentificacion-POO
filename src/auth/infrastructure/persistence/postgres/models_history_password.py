from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, DateTime
from datetime import datetime
from sqlalchemy import Column, text

if TYPE_CHECKING:
    from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser

class HistoryPassword(SQLModel, table=True):
    __tablename__ = "history_password"

    id_history_password: Optional[int] = Field(default=None, primary_key=True)
    
    password_hash_anterior: str = Field(unique=True, index=True, nullable=False, max_length=255)
    fecha_cambio: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)

    usuario: Optional["AuthUser"] = Relationship(
        back_populates="history_password"
    )



class HisoryPasswordNoTable(SQLModel):
    id_history_password: Optional[int] = Field(default=None, primary_key=True)
    password_hash_anterior: str = Field(unique=True, index=True, nullable=False, max_length=255)
    fecha_cambio: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)

