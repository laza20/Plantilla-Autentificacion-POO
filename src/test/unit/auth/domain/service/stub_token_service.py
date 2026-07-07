class StubTokenService:

    def create_access_token(self, user_id: int) -> str:
        """
        Función para simular la creación de un token de acceso.
        """
        return f"access_token_{user_id}"

