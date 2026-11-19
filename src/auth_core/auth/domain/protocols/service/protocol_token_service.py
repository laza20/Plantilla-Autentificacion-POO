from typing import Protocol, runtime_checkable
from auth_core.auth.domain.entities.entitie_auth_users import UserTokens


@runtime_checkable
class TokenProtocol(Protocol):
    """
    Contrato para servicios de tokens de autenticación.

    Define la interfaz que cualquier servicio de tokens debe cumplir (JWT, etc.).
    Cubre los tokens de sesión (access / refresh) y los tokens de scope único
    para flujos puntuales (reset, verificación, eliminación, reactivación).

    Cómo implementar:
        1. Crear una clase con los métodos de este contrato, respetando las firmas.
        2. Registrarla en dependencies.py.

    Los métodos privados (ej. _encode_token) no forman parte del contrato:
    cada implementación puede tener sus propios helpers.

    Convenciones (implementación JWT):
        - El user_id viaja en el claim "sub".
        - El claim "type" identifica el scope del token ("access", "refresh",
          "reset", "verification", "eliminacion", "reactivacion").
        - Un token solo es válido en el flujo de su propio scope.
        - Los métodos get_* son stateless: no consultan la BD.
        - Token inválido, expirado o de otro scope -> TokenInvalido.

    Atributos requeridos: ninguno.
    """

    def create_user_tokens(self, user_id: int) -> UserTokens:
        """
        Crea el par de tokens de sesión de un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            UserTokens con access_token y refresh_token.
        """
        ...

    def create_access_token(self, user_id: str) -> str:
        """
        Crea un token de acceso de corta duración.

        Args:
            user_id: ID del usuario (típicamente str(usuario.id_usuario)).

        Returns:
            Token firmado con scope "access".
            - Duración corta (configurable, ej. 15 minutos).
            - Se envía en cada request autenticado.
            - No requiere logout: expira solo.

        Ciclo de vida:
            1. Login -> se emite junto al refresh token.
            2. El cliente lo envía en cada request.
            3. El servidor lo valida con get_user_id_from_access_token().
            4. Al expirar, el cliente usa el refresh token para obtener uno nuevo.
        """
        ...

    def create_refresh_token(self, user_id: str) -> str:
        """
        Crea un token de refresco de larga duración.

        Args:
            user_id: ID del usuario (típicamente str(usuario.id_usuario)).

        Returns:
            Token firmado con scope "refresh".
            - Duración larga (configurable, ej. 7 días).
            - Se guarda en cookie HttpOnly.
            - Solo se usa en el endpoint de refresh para obtener un nuevo access token.
            - Su hash (ver hash_token) se persiste en la tabla de sesiones.
        """
        ...

    def get_user_id_from_access_token(self, token: str) -> int:
        """
        Valida un access token y devuelve el user_id.

        Args:
            token: Token generado por create_access_token().

        Returns:
            ID del usuario como int.

        Raises:
            SinAccessToken: si el token es válido pero no es de scope "access"
                (ej. se envió un refresh token).
            TokenInvalido: si el token está malformado, expiró, o no contiene "sub".

        Ejemplo en un endpoint protegido:
            try:
                user_id = token_service.get_user_id_from_access_token(token)
            except TokenInvalido:
                raise HTTPException(status_code=401, detail="Token inválido o expirado")
        """
        ...

    def get_user_id_from_refresh_token(self, token: str) -> str:
        """
        Valida un refresh token y devuelve el user_id.

        Args:
            token: Token generado por create_refresh_token(),
                normalmente leído de la cookie HttpOnly.

        Returns:
            ID del usuario como str (valor del claim "sub").

        Raises:
            TokenInvalido: si el token está malformado, expiró, no es de scope
                "refresh" o no contiene "sub". Ante esto el usuario debe
                iniciar sesión nuevamente.

        Ejemplo en AuthService.refreshed_token():
            user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)
            nuevo_access = self.token_service.create_access_token(user_id)
        """
        ...

    def hash_token(self, token: str) -> str:
        """
        Genera un hash irreversible y determinístico de un token en texto plano.

        Args:
            token: Token en texto plano (ej. refresh token).

        Returns:
            Hash del token, apto para persistir.

        Uso:
            - Guardar una representación segura del refresh token en la tabla
              de sesiones, sin almacenar el token crudo.
            - Recalcular el hash del token recibido en la cookie para buscar
              y eliminar la sesión correspondiente (ej. en el logout).
            - Al ser determinístico, el mismo token siempre produce el mismo hash.
        """
        ...

    def generar_token_plano(self) -> str:
        """
        Genera un token opaco criptográficamente seguro (no JWT).

        Pensado para flujos que envían un valor plano por correo y guardan
        solo su hash en la BD (ej. recuperación de contraseña), a diferencia
        de los JWT autocontenidos del resto del servicio.

        Returns:
            Token URL-safe con 32 bytes de entropía.
        """
        ...

    def create_reset_token(self, user_id: str) -> str:
        """
        Crea un JWT de scope "reset" para el cambio de contraseña.

        Se emite tras verificar el token plano de recuperación y habilita
        únicamente el último paso del flujo (cambiar la contraseña).

        Args:
            user_id: ID del usuario que recupera su contraseña.

        Returns:
            JWT firmado, con expiración RESET_PASSWORD_TOKEN_EXPIRE_MINUTES.
        """
        ...

    def get_current_reset_scope(self, token: str) -> str:
        """
        Valida un JWT de scope "reset" y devuelve el user_id.

        Args:
            token: JWT emitido por create_reset_token().

        Returns:
            ID del usuario (claim "sub").

        Raises:
            TokenInvalido: si el token es inválido, expiró, no es de scope
                "reset" o no contiene "sub".
        """
        ...

    def create_verificacion_token(self, user_id: str) -> str:
        """
        Crea un JWT de scope "verification" para activar una cuenta.

        Se envía por correo al registrarse o al reenviar el mail de activación.

        Args:
            user_id: ID del usuario a verificar.

        Returns:
            JWT firmado, con expiración VERIFY_MAIL_RECUPERACION.
        """
        ...

    def get_user_id_from_verificacion_token(self, token: str) -> str:
        """
        Valida un JWT de scope "verification" y devuelve el user_id.

        Args:
            token: JWT emitido por create_verificacion_token().

        Returns:
            ID del usuario (claim "sub").

        Raises:
            TokenInvalido: si el token es inválido, expiró, no es de scope
                "verification" o no contiene "sub".
        """
        ...

    def create_eliminacion_token(self, user_id: str) -> str:
        """
        Crea un JWT de scope "eliminacion" para confirmar la baja de la cuenta.

        Args:
            user_id: ID del usuario a dar de baja.

        Returns:
            JWT firmado, con expiración ELIMINACION_CUENTA.
        """
        ...

    def get_user_id_from_eliminacion_token(self, token: str) -> str:
        """
        Valida un JWT de scope "eliminacion" y devuelve el user_id.

        Args:
            token: JWT emitido por create_eliminacion_token().

        Returns:
            ID del usuario (claim "sub").

        Raises:
            TokenInvalido: si el token es inválido, expiró, no es de scope
                "eliminacion" o no contiene "sub".
        """
        ...

    def create_reactivacion_token(self, user_id: str) -> str:
        """
        Crea un JWT de scope "reactivacion" para reactivar una cuenta dada de baja.

        Args:
            user_id: ID del usuario a reactivar.

        Returns:
            JWT firmado, con expiración REACTIVACION_CUENTA.
        """
        ...

    def get_user_id_from_reactivacion_token(self, token: str) -> str:
        """
        Valida un JWT de scope "reactivacion" y devuelve el user_id.

        Args:
            token: JWT emitido por create_reactivacion_token().

        Returns:
            ID del usuario (claim "sub").

        Raises:
            TokenInvalido: si el token es inválido, expiró, no es de scope
                "reactivacion" o no contiene "sub".
        """
        ...