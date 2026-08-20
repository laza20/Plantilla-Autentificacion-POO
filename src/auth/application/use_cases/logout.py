from fastapi import Response
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.protocol_sesion_repository import TokenRepositoryProtocol

class LogoutUseCase:
    def __init__(
        self,
        cookies_service: CookiesService,
        token_service: TokenProtocol,
        token_repository: TokenRepositoryProtocol
    ):
        self.cookies_service = cookies_service
        self.token_service = token_service
        self.token_repository = token_repository

    def ejecutar(self, refresh_token: str, response: Response):
        """
        Servicio para deslogear a un usuario.
        """
        hashed_token = self.token_service.hash_token(refresh_token)
        self.token_repository.eliminar_por_hash(hashed_token)
        self.cookies_service.delete_auth_cookies(response)
