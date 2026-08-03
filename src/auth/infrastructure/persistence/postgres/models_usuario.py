from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .models_auth_users import AuthUser

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id_usuario: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key="auth_users.id_usuario"
    )

    auth_user: Optional["AuthUser"] = Relationship(
        back_populates="usuario"
    )