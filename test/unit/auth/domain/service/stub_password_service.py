class StubPasswordService:
    def hash_password(self, password: str) -> str:
        """
        Función para simular el hashing de una contraseña.
        """
        return f"hashed_{password}"


    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Función para simular la verificación de una contraseña.
        """
        return f"hashed_{password}" == hashed_password
