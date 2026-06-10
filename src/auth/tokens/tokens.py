from datetime import timedelta
from src.auth.security import security
from fastapi import Body
from src.exceptions.usuarios_exceptions import TokenInvalido
from jose import JWTError
from src.config.config import settings


def create_access_token(user_id: str) -> str:
    """
    Funcion encargada de crear un access token para un usuario dado su id.
    El access token tiene una duración corta y se utiliza para autenticar las solicitudes del usuario.
    """
    return security.encode_token(
        {
            "sub": str(user_id),
            "type": "access"
        },
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: str) -> str:
    """
    Funcion encarcargada de crear un refresh token para un usuario dado su id.
    El refresh token tiene una duración más larga que el access token y se utiliza para obtener nuevos
    """
    return security.encode_token(
        {
            "sub": str(user_id),
            "type": "refresh"
        },
        timedelta(days=settings.REFRESH_TOKEN_DURATION)
    )


def refreshed_token(refresh_token: str = Body(...)):
    """
    Servicio para refrescar el access token usando un refresh token válido.
    """
    try:
        payload = security.decode_token(refresh_token)

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalido("Refresh token inválido")

    except JWTError as e:
        raise TokenInvalido("Refresh token inválido o expirado")

    new_access_token = create_access_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }