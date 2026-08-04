from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models_sesiones import SesionesNoTable as Sesion


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
        id_usuario: int,
        ip: str
    ) -> list[Sesion]: ...

    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None: ...


    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:...