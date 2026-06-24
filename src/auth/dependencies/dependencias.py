from fastapi import HTTPException, Request, Depends
from jose import JWTError
from src.auth.tokens.tokens import TokenService, get_token_service
from src.config.config import get_settings, Settings
from src.auth.repository import UserRepository, get_user_repository
from src.auth.models import AuthUser
from src.exceptions.usuarios_exceptions import (
    NoAutenticado, SinAccessToken, TokenInvalido, UsuarioNoEncontrado
)


class AuthDependencies:
    def __init__(
        self,
        settings: Settings,
        token_service: TokenService,
        user_repository: UserRepository
    ):
        self.settings = settings
        self.token_service = token_service
        self.user_repository = user_repository

    async def get_current_user(
        self, 
        request: Request
    ) -> AuthUser:
        """Obtiene el usuario actual del token en cookies."""
        token = request.cookies.get("access_token")

        if not token:
            raise NoAutenticado("Usuario no autenticado")

        try:
            payload = self.token_service.decode_token(token)
            if payload.get("type") != "access":
                raise SinAccessToken("Se proporcionó un Refresh Token")

            user_id = payload.get("sub")
            if not user_id:
                raise TokenInvalido("Token inválido: falta el sub")

        except JWTError:
            raise TokenInvalido("Token inválido o expirado")

        try:
            usuario = self.user_repository.obtener_por_id(user_id)
            return usuario
        except UsuarioNoEncontrado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

    async def get_admin_user(
        self, 
        request: Request
    ) -> AuthUser:
        """Obtiene el usuario actual y valida que sea admin."""
        user = await self.get_current_user(request)
        
        if user.role != "admin":
            raise HTTPException(
                status_code=403, 
                detail="Se requieren permisos de administrador"
            )
        
        return user

    async def get_premium_user(
        self, 
        request: Request
    ) -> AuthUser:
        """Obtiene el usuario actual y valida que sea premium."""
        user = await self.get_current_user(request)
        
        if not user.is_premium:
            raise HTTPException(
                status_code=403, 
                detail="Se requiere suscripción premium"
            )
        
        return user


def get_auth_dependencies(
    settings: Settings = Depends(get_settings),
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthDependencies:
    """Factory para inyectar AuthDependencies en endpoints."""
    return AuthDependencies(
        settings=settings,
        token_service=token_service,
        user_repository=user_repository
    )


async def get_current_user(
    request: Request,
    auth_deps: AuthDependencies = Depends(get_auth_dependencies)
) -> AuthUser:
    """Dependencia que retorna el usuario actual."""
    return await auth_deps.get_current_user(request)


async def get_admin_user(
    request: Request,
    auth_deps: AuthDependencies = Depends(get_auth_dependencies)
) -> AuthUser:
    """Dependencia que retorna el usuario actual si es admin."""
    return await auth_deps.get_admin_user(request)


async def get_premium_user(
    request: Request,
    auth_deps: AuthDependencies = Depends(get_auth_dependencies)
) -> AuthUser:
    """Dependencia que retorna el usuario actual si es premium."""
    return await auth_deps.get_premium_user(request)