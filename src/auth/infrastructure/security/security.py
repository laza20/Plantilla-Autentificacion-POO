from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

class PasswordService:
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

