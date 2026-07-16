class StubTokenService:
    def __init__(self):
        self.fue_llamado = False
        self.user_id_recibido = None
        self.token_generado = None

    def create_access_token(self, user_id: int) -> str:
        """
        Función para simular la creación de un token de acceso.
        """
        self.fue_llamado = True
        self.user_id_recibido = int(user_id)
        self.token_generado = f"access_token_{user_id}"
        return self.token_generado
