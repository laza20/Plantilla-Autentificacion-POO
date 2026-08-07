from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models_sesiones import SesionesVisual as Sesiones


@runtime_checkable
class TokenRepositoryProtocol(Protocol):
    def insertar_sesion(
        self,
        hash_token: str,
        id_usuario: int,
        ip: str,
        user_agent: str
    ) -> None: ...

    def listar_sesiones(
        self,
        id_usuario: int
    ) -> list[Sesiones]: ...

    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None: ...


    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:...