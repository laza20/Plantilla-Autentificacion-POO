from typing import Protocol, runtime_checkable
from src.auth.models import AuthUser

@runtime_checkable
class UserRepositoryProtocol(Protocol):

    def insertar(self, usuario:AuthUser)-> AuthUser:
        ...

    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        ...

    def activar(self, usuario: AuthUser) -> AuthUser:
        ...

    def obtener_por_email(self, email: str) -> AuthUser | None:
        ...

    def obtener_por_id(self, id_usuario:int) -> AuthUser | None:
        ...
