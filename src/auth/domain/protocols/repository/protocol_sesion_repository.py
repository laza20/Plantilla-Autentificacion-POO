from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models.models_sesiones import SesionesVisual as Sesiones


@runtime_checkable
class TokenRepositoryProtocol(Protocol):
    """Contrato de persistencia para la tabla `sesiones`, usado en listado
    y revocación de sesiones multi-dispositivo del usuario. Separado de
    `TokenProtocol` (que solo maneja criptografía de tokens, sin acceso
    a BD).
    """

    def insertar_sesion(
        self,
        hash_token: str,
        id_usuario: int,
        ip: str,
        user_agent: str
    ) -> None:
        """Registra una nueva sesión al iniciar login.

        Args:
            hash_token: Hash (vía hash_token()) del refresh_token de la sesión.
            id_usuario: ID del usuario dueño de la sesión.
            ip: IP del cliente al momento del login.
            user_agent: User agent del cliente al momento del login.
        """
        ...

    def listar_sesiones(
        self,
        id_usuario: int
    ) -> list[Sesiones]:
        """Devuelve todas las sesiones registradas de un usuario.

        Args:
            id_usuario: ID del usuario cuyas sesiones se listan.

        Returns:
            Lista de sesiones (posiblemente vacía).
        """
        ...

    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None:
        """Elimina una sesión puntual, para revocación manual desde el listado.

        Args:
            id_sesion: ID de la sesión a eliminar.
            id_usuario: ID del usuario dueño de la sesión, para evitar que
                un usuario elimine sesiones ajenas.
        """
        ...

    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:
        """Elimina la sesión asociada a un refresh_token, usado en logout.

        Args:
            hash_token: Hash (vía hash_token()) del refresh_token de la sesión
                a eliminar.
        """
        ...

    def eliminar_todas_las_sesiones_de_un_usuario(self, id_usuario: int) -> bool | None:
        """Elimina todas las sesiones de un usuario (ej. al cambiar contraseña
        o eliminar la cuenta).

        Args:
            id_usuario: ID del usuario cuyas sesiones se eliminan.

        Returns:
            True si eliminó al menos una sesión, False si no había ninguna.
        """
        ...