from fastapi import Response
from src.auth.cookies.cookies import CookiesService

class LogoutUseCase:
    def __init__(
        self,
        cookies_service: CookiesService
    ):
        self.cookies_service = cookies_service

    def logout(self, response:Response):
        """
        Servicio para deslogear a un usuario.
        """
        self.cookies_service.delete_auth_cookies(response)

