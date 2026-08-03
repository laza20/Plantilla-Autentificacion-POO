from datetime import datetime, timezone, timedelta
from jose import jwt
from typing import Dict
from src.auth.domain.exceptions.tokens import TokenInvalido
from jose import JWTError
from fastapi import Depends
from src.config.config import get_settings, Settings
from auth.infrastructure.persistence.postgres.models_auth_users import UserTokens


class TokenService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create_user_tokens(self, user_id:int) -> UserTokens:

        return UserTokens(
            access_token=self.create_access_token(str(user_id)),
            refresh_token=self.create_refresh_token(str(user_id))
        )

    def create_access_token(self, user_id: str) -> str:
        """
        Funcion encargada de crear un access token para un usuario dado su id.
        El access token tiene una duración corta y se utiliza para autenticar las solicitudes del usuario.
        """
        return self._encode_token(
            {
                "sub": str(user_id),
                "type": "access"
            },
            timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )


    def create_refresh_token(self, user_id: str) -> str:
        """
        Funcion encarcargada de crear un refresh token para un usuario dado su id.
        El refresh token tiene una duración más larga que el access token y se utiliza para obtener nuevos
        """
        return self._encode_token(
            {
                "sub": str(user_id),
                "type": "refresh"
            },
            timedelta(days=self.settings.REFRESH_TOKEN_DURATION)
        )


    def decode_token(self, token: str) -> Dict[str, any]:
        """
        Funcion encargada de decodificar un token JWT utilizando la clave secreta y el algoritmo especificados en la configuración.
        - El token se decodifica utilizando la clave secreta y el algoritmo especificados en la configuración.
        - Si el token es válido, se devuelve el payload decodificado.
        - Si el token es inválido o ha expirado, se lanza una excepción JWTError.
        """
        try:
            return jwt.decode(token, self.settings.JWT_SECRET_KEY, algorithms=[self.settings.ALGORITHM])
        except JWTError as e:
            raise TokenInvalido(
                "Token inválido o expirado"
            ) from e
        
    def get_user_id_from_access_token(self, token:str)->int:
        try:
            payload = self.decode_token(token)
            
            if payload.get("type") != "access":
                raise TokenInvalido()
                        
            user_id = payload.get("sub")
            if not user_id:
                raise TokenInvalido()
            
            return int(user_id)

        except JWTError:
            raise TokenInvalido()
        
    def get_user_id_from_refresh_token(self, token:str)->str:
        try:
            payload = self.decode_token(token)

            user_id = payload.get("sub")
            if not user_id:
                raise TokenInvalido("Refresh token inválido")
            
            return user_id

        except JWTError as e:
            raise TokenInvalido("Refresh token inválido o expirado")


    def _encode_token(self, payload: Dict[str, any], expires_delta: timedelta) -> str:
        """
        Funcion encargada de codificar un token JWT utilizando la clave secreta y el algoritmo especificados en la configuración.
        - El token se firma utilizando la clave secreta y el algoritmo especificados en la configuración.
        - El token incluye una fecha de expiración calculada a partir del tiempo actual y el tiempo de expiración proporcionado.
        """
        data = payload.copy()
        data["exp"] = self._obtener_tiempo_expiracion(expires_delta)
        return jwt.encode(data, self.settings.JWT_SECRET_KEY, algorithm=self.settings.ALGORITHM)


    def _obtener_tiempo_expiracion(self, expires_delta:timedelta)->int:
        expire = datetime.now(timezone.utc) + expires_delta
        return int(expire.timestamp())

    
def get_token_service(settings: Settings = Depends(get_settings)) -> TokenService:
    return TokenService(settings=settings)