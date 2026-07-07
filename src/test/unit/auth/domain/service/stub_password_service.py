class StubPasswordService:
    def hash_password(self, password: str) -> str:
        """
        Función para simular el hashing de una contraseña.
        """
        return f"hashed_{password}"
