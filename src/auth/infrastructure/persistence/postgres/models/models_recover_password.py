from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, DateTime
from datetime import datetime
from sqlalchemy import Column, text

if TYPE_CHECKING:
    from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser

class RecoverPassword(SQLModel, table=True):
    __tablename__ = "recover_password"

    id_recover_password: Optional[int] = Field(default=None, primary_key=True)
    
    token_hash: str = Field(unique=True, index=True, nullable=False, max_length=255)
    expira_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))
    usado: bool = Field(default=False)
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)

    usuario: Optional["AuthUser"] = Relationship(
        back_populates="recover_password"
    )


class RecoverPasswordNoTable(SQLModel):
    id_recover_password: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(unique=True, index=True, nullable=False, max_length=255)
    expira_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))
    usado: bool = Field(default=False)
    id_usuario: int = Field(foreign_key="auth_users.id_usuario",nullable=False)