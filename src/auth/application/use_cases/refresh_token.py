from fastapi import Response
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.exceptions.tokens import TokenInvalido, VerificacionInvalida

class RefreshTokenUseCase:
    def __init__(
        self,
        token_service: TokenProtocol,
        cookies_service: CookiesService
    ):
        self.token_service = token_service
        self.cookies_service = cookies_service

    def ejecutar(self, refresh_token: str, response:Response):
        """
        Servicio para refrescar el access token usando un refresh token válido.
        """
        try:
            user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)
        except TokenInvalido:
            raise VerificacionInvalida()

        new_access_token = self.token_service.create_access_token(user_id)

        self.cookies_service.set_access_cookie(response, new_access_token)

