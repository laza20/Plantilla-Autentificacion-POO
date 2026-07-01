from pwdlib import PasswordHash
from src.config.config import Settings, get_settings
from fastapi import Depends

pwd_context = PasswordHash.recommended()

class PasswordService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def hash_password(self, password: str) -> str:
        """
        Funcion encargada de realizar el hasheo de la contraseña proporsionada por el usuario
        - utiliza argon2 como algoritmo de hashing.
        """
        return pwd_context.hash(password)


    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Funcion encargada de verificar la contraseña proporcionada por el usuario contra la contraseña hasheada.
        - utiliza argon2 como algoritmo de hashing.
        """
        return pwd_context.verify(plain, hashed)


def get_password_service(settings: Settings = Depends(get_settings)) -> PasswordService:
    return PasswordService(settings=settings)