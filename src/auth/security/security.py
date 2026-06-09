from pwdlib import PasswordHash
from src.config.config import settings
from datetime import datetime, timedelta, timezone
from jose import jwt

pwd_context = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Funcion encargada de realizar el hasheo de la contraseña proporsionada por el usuario
    - utiliza argon2 como algoritmo de hashing.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Funcion encargada de verificar la contraseña proporcionada por el usuario contra la contraseña hasheada.
    - utiliza argon2 como algoritmo de hashing.
    """
    return pwd_context.verify(plain, hashed)

def encode_token(payload: dict, expires_delta: timedelta) -> str:
    """
    Funcion encargada de codificar un token JWT utilizando la clave secreta y el algoritmo especificados en la configuración.
    - El token se firma utilizando la clave secreta y el algoritmo especificados en la configuración.
    - El token incluye una fecha de expiración calculada a partir del tiempo actual y el tiempo de expiración proporcionado.
    """
    data = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    data["exp"] = int(expire.timestamp())
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Funcion encargada de decodificar un token JWT utilizando la clave secreta y el algoritmo especificados en la configuración.
    - El token se decodifica utilizando la clave secreta y el algoritmo especificados en la configuración.
    - Si el token es válido, se devuelve el payload decodificado.
    - Si el token es inválido o ha expirado, se lanza una excepción JWTError.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])