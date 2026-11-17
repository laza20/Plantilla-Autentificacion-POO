from typing import Protocol, runtime_checkable
from src.auth.domain.entities.entitie_auth_users import AuthUser
from datetime import datetime

@runtime_checkable
class AuthUserRepositoryProtocol(Protocol):
    """
    Contrato de persistencia de usuarios de autenticación.

    Lo consumen los casos de uso de auth (registro, verificación de email,
    login, recuperación de contraseña, baja y reactivación de cuenta). La
    implementación concreta vive fuera del dominio y se arma en la composition
    root (src/container/auth/providers.py).

    Estados del usuario (EstadoEntidad): PENDIENTE (registrado, sin verificar),
    ACTIVO y ELIMINADO (baja lógica). Cada método indica sobre cuáles busca.

    No se asume commit al retornar: la confirmación de la transacción no es
    responsabilidad de estos métodos.
    """

    def insertar(self, usuario: AuthUser) -> AuthUser:
        """
        Inserta un usuario nuevo y devuelve la entidad persistida.

        Args:
            usuario: Entidad a insertar. El password debe llegar ya hasheado.

        Returns:
            La entidad con los datos persistidos, incluido el id_usuario asignado.

        Raises:
            MailRepetido: Si ya existe un usuario con ese email, sin importar
                su estado (PENDIENTE, ACTIVO o ELIMINADO).
        """
        ...

    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        """
        Busca un usuario por id sin filtrar por estado.

        Sirve para resolver usuarios que todavía no están ACTIVOS (por ejemplo,
        al verificar el email). obtener_por_id y obtener_por_email, en cambio,
        solo devuelven usuarios ACTIVOS.

        Args:
            id_usuario: ID del usuario.

        Returns:
            El usuario, o None si no existe.
        """
        ...

    def activar(self, usuario: AuthUser) -> AuthUser:
        """
        Marca al usuario como verificado y ACTIVO.

        Cambia estado a EstadoEntidad.ACTIVO e is_verified a True, y devuelve
        el usuario con el cambio aplicado. El cambio debe quedar reflejado en
        la persistencia al cerrarse la transacción. Es una transición de un
        solo sentido: no vuelve a PENDIENTE.

        Args:
            usuario: Usuario obtenido con obtener_por_id_sin_activar.

        Returns:
            El mismo usuario, ya activado.
        """
        ...

    def obtener_por_email(self, email: str) -> AuthUser | None:
        """
        Busca un usuario ACTIVO por email (p. ej. para el login).

        No devuelve usuarios PENDIENTES ni ELIMINADOS.

        Args:
            email: Email exacto a buscar.

        Returns:
            El usuario ACTIVO, o None si no existe o no está ACTIVO.
        """
        ...

    def obtener_por_id(self, id_usuario: int) -> AuthUser | None:
        """
        Busca un usuario ACTIVO por id.

        No devuelve usuarios PENDIENTES ni ELIMINADOS.

        Args:
            id_usuario: ID del usuario.

        Returns:
            El usuario ACTIVO, o None si no existe o no está ACTIVO.
        """
        ...

    def modificar_contraseña(
            self, 
            id_usuario: int, 
            contraseña_nueva: str,
            fecha_actual: datetime) -> bool:
        """
        Actualiza el hash de contraseña de un usuario verificado.

        Se usa en el paso final de la recuperación de contraseña. Solo afecta
        a usuarios con is_verified = True.

        Args:
            id_usuario: ID del usuario cuya contraseña se modifica.
            contraseña_nueva: Hash de la nueva contraseña (nunca en claro).
            fecha_actual: Valor a guardar en updated_at.

        Returns:
            True si actualizó un registro; False si no hay un usuario
            verificado con ese id_usuario.
        """
        ...

    def obtener_por_email_sin_activar(self, email: str) -> AuthUser | None:
        """
        Busca un usuario PENDIENTE por email.

        Sirve, por ejemplo, para reenviar el mail de verificación. No devuelve
        usuarios ACTIVOS ni ELIMINADOS.

        Args:
            email: Email exacto a buscar.

        Returns:
            El usuario PENDIENTE, o None si no existe o está en otro estado.
        """
        ...


    def modificar_usuario(self, usuario: AuthUser) -> AuthUser | None:
        """
        Sobrescribe los datos persistidos de un usuario existente.

        Escribe todos los campos de la entidad excepto id_usuario, que solo
        identifica el registro. Una entidad incompleta pisa los valores
        guardados, por lo que debe llegar completa.

        Args:
            usuario: Entidad completa, con id_usuario.

        Returns:
            La entidad con los datos aplicados, o None si no existe un registro
            con ese id_usuario.
        """
        ...

    def eliminar_usuario(self, usuario: AuthUser) -> bool | None:
        """
        Persiste la baja lógica de un usuario.

        No borra el registro. Escribe los campos de la entidad tal como llegan
        (incluido el estado), por lo que el consumidor debe marcarla como
        eliminada (estado ELIMINADO) antes de llamar.

        Args:
            usuario: Entidad ya marcada como eliminada, con id_usuario.

        Returns:
            True si actualizó un registro; False si no existe ese id_usuario.
        """
        ...

    def obtener_usuario_eliminado_por_mail(self, mail_usuario:str)->AuthUser | None:
        """
        Busca un usuario ELIMINADO (baja lógica) por email.

        Args:
            mail_usuario: Email exacto a buscar.

        Returns:
            El usuario ELIMINADO, o None si no existe o no está ELIMINADO.
        """
        ...

    def obtener_usuario_eliminado_por_id(self, id_usuario:int)->AuthUser | None:
        """
        Busca un usuario ELIMINADO (baja lógica) por id.

        Args:
            id_usuario: ID del usuario.

        Returns:
            El usuario ELIMINADO, o None si no existe o no está ELIMINADO.
        """
        ...

    def activar_usuario_eliminado(self, id_usuario:int)-> bool | None:
        """
        Reactiva un usuario dado de baja.

        Pasa el estado de ELIMINADO a ACTIVO y limpia eliminado_en. No modifica
        is_verified. Solo afecta a registros ELIMINADOS.

        Args:
            id_usuario: ID del usuario a reactivar.

        Returns:
            True si reactivó un registro; False si no hay un usuario ELIMINADO
            con ese id_usuario.
        """
        ...