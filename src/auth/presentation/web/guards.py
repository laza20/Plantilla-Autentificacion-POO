from fastapi import Request
from src.config.config import Settings
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.usuarios_exceptions import (NoAutenticado, UsuarioNoEncontrado)
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.exceptions.tokens import TokenInvalido


class AuthDependencies:
    def __init__(
        self,
        settings: Settings,
        token_service: TokenProtocol,
        auth_user_repository: AuthUserRepositoryProtocol
    ):
        self.settings = settings
        self.token_service = token_service
        self.auth_user_repository = auth_user_repository

    async def get_current_user(
        self, 
        request: Request
    ) -> AuthUser:
        """Obtiene el usuario actual del token en cookies."""
        token = request.cookies.get("access_token")

        if not token:
            raise NoAutenticado("Usuario no autenticado")

        user_id = self.token_service.get_user_id_from_access_token(token)
        if not user_id:
            raise TokenInvalido("Token inválido: falta el sub")

        usuario = self.auth_user_repository.obtener_por_id(user_id)
        if not usuario:
            raise UsuarioNoEncontrado("Usuario no encontrado")

        return usuario

    async def get_admin_user(
        self, 
        request: Request
    ) -> AuthUser:
        """
        Obtiene el usuario actual y valida que sea admin.
        TODO: 'role' no existe todavía en AuthUser — pendiente de agregar
        cuando se implemente el sistema de roles.
        """
        raise NotImplementedError("get_admin_user: falta el campo 'role' en AuthUser")
        #user = await self.get_current_user(request)
        #if user.role != "admin":  # AttributeError hasta que exista el campo
        #    raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        #return user
        


    async def get_premium_user(
        self, 
        request: Request
    ) -> AuthUser:
        """
        Obtiene el usuario actual y valida que sea premium.
        TODO: 'role' no existe todavía en AuthUser — pendiente de agregar
        cuando se implemente el sistema de roles.
        """
        raise NotImplementedError("get_premium_user: falta el campo 'role' en AuthUser")
        #user = await self.get_current_user(request)
        #if user.role != "premium":  # AttributeError hasta que exista el campo
        #    raise HTTPException(status_code=403, detail="Se requieren permisos de premium")
        #return user


