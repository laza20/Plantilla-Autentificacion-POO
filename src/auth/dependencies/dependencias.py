from fastapi import HTTPException, Request
from jose import JWTError
from src.auth.security.security import decode_token
from src.auth import repository
from sqlmodel import Session
from fastapi import Depends
from src.database.client import get_session
from src.exceptions.usuarios_exceptions import (
    UsuarioNoEncontrado, NoAutenticado, 
    SinAccessToken, TokenInvalido)
from src.config.config import Settings, settings

def get_settings() -> Settings:
    return settings


async def get_current_user(request: Request, session: Session = Depends(get_session)):
        token = request.cookies.get("access_token")

        if not token:
            raise NoAutenticado("Usuario no autenticado")

        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise SinAccessToken("Se proporcionó un Refresh Token en lugar de un Access Token")

            user_id = payload.get("sub")
            if not user_id:
                raise TokenInvalido("Token inválido: falta el sub")


        except JWTError:
            raise TokenInvalido("Token inválido o expirado")

        try:
            usuario = repository.obtener_user_por_id(session, user_id)
            return usuario
        except UsuarioNoEncontrado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")