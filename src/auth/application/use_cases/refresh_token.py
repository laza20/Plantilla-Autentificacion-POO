from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.exceptions.tokens import TokenInvalido, VerificacionInvalida

class RefreshTokenUseCase:
    def __init__(
        self,
        token_service: TokenProtocol
    ):
        self.token_service = token_service

    def ejecutar(self, refresh_token: str):
        """
        Servicio para refrescar el access token usando un refresh token válido.
        """
        try:
            user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)
        except TokenInvalido:
            raise VerificacionInvalida()

        return self.token_service.create_access_token(user_id)