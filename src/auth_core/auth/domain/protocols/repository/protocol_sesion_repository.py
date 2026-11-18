from typing import Protocol, runtime_checkable
from auth_core.auth.domain.entities.entitie_sesiones import Sesion


@runtime_checkable
class TokenRepositoryProtocol(Protocol):
    """Contrato de persistencia de sesiones de usuario (una por refresh token emitido).

    Lo consumen los casos de uso de login, logout y gestión de sesiones
    multi-dispositivo (listado y revocación). Guarda solo el hash del refresh
    token, nunca el token en claro. No genera ni valida tokens: eso lo hace el
    servicio de tokens. La implementación concreta vive fuera del dominio y se
    arma en la composition root (src/container/auth/providers.py).
    """

    def insertar_sesion(
        self,
        hash_token: str,
        id_usuario: int,
        ip: str,
        user_agent: str
    ) -> None:
        """Registra una nueva sesión al iniciar sesión (login). No devuelve valor.

        Args:
            hash_token: Hash del refresh token de la sesión.
            id_usuario: ID del usuario dueño de la sesión.
            ip: IP del cliente al momento del login.
            user_agent: User agent del cliente al momento del login.
        """
        ...

    def listar_sesiones(
        self,
        id_usuario: int
    ) -> list[Sesion]:
        """Devuelve todas las sesiones registradas de un usuario.

        Args:
            id_usuario: ID del usuario cuyas sesiones se listan.

        Returns:
            Lista de sesiones (vacía si no tiene ninguna).
        """
        ...

    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None:
        """Elimina una sesión puntual (revocación manual desde el listado).

        No hace nada, sin error, si la sesión no existe o pertenece a otro
        usuario.

        Args:
            id_sesion: ID de la sesión a eliminar.
            id_usuario: ID del usuario dueño de la sesión; evita que un
                usuario elimine sesiones ajenas.
        """
        ...

    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:
        """Elimina la sesión asociada a un refresh token (logout).

        No hace nada, sin error, si no existe una sesión con ese hash.

        Args:
            hash_token: Hash del refresh token de la sesión a eliminar.
        """
        ...

    def eliminar_todas_las_sesiones_de_un_usuario(self, id_usuario: int) -> bool | None:
        """Elimina todas las sesiones de un usuario (p. ej. al cambiar la
        contraseña o eliminar la cuenta).

        Args:
            id_usuario: ID del usuario cuyas sesiones se eliminan.

        Returns:
            True si eliminó al menos una sesión; False si no había ninguna.
        """
        ...