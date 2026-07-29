from src.auth.infrastructure.persistence.postgres.models import UserTokens
from src.auth.domain.exceptions.usuarios_exceptions import TokenInvalido
from jose import JWTError


class StubTokenService:
    def __init__(self):
        self.fue_llamado = False
        self.user_id_recibido = None
        self.access_token_generado = None
        self.refresh_token_generado = None

    def _actualizar_llamada(self, user_id: int):
        self.fue_llamado = True
        self.user_id_recibido = user_id

    def create_access_token(self, user_id: int) -> str:
        """
        Función para simular la creación de un token de acceso.
        """
        if not self.fue_llamado:
            self._actualizar_llamada(user_id)
        self.access_token_generado = f"access_token_{user_id}"
        return self.access_token_generado

    def create_refresh_token(self, user_id: int) -> str:
        """
        Función para simular la creación de un token de actualización.
        """
        if not self.fue_llamado:
            self._actualizar_llamada(user_id)
        self.refresh_token_generado = f"refresh_token_{user_id}"
        return self.refresh_token_generado

    def create_user_tokens(self, user_id:int) -> UserTokens:
        return UserTokens(
            access_token=self.create_access_token(user_id),
            refresh_token=self.create_refresh_token(user_id)
        )
    
    def get_user_id_from_access_token(self, token:str)->int:
        try:

            tipo, token, user_id  = token.split("_")
            
            if tipo != "access" or token != "token":
                raise TokenInvalido()
            
            return int(user_id)

        except (ValueError, IndexError):
            raise TokenInvalido()