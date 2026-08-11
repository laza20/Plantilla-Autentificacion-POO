from src.auth.infrastructure.persistence.postgres.models_auth_users import UserTokens
from fastapi import Response
import logging
from src.auth.domain.protocols.auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.exceptions.tokens import TokenInvalido, VerificacionInvalida
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.infrastructure.security.security import Settings
from src.auth.presentation.web.cookies.cookies import CookiesService



logger = logging.getLogger(__name__)

class VerifyMailUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        settings : Settings,
        cookies_service: CookiesService,
        token_service: TokenProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.settings = settings
        self.cookies_service = cookies_service
        self.token_service = token_service

    def ejecutar(self, token: str, response:Response)-> UserTokens:
        """
        Funcion encargada de verificar el mail del usuario utilizando un token de verificación.
        El token se decodifica para obtener el ID del usuario, luego se busca el usuario en la base de datos y se activa su cuenta.
        Si el token es inválido o el usuario no existe, se lanzan excepciones correspondientes
        """
        try:
            user_id_db = self.token_service.get_user_id_from_access_token(token)
            usuario = self.auth_user_repository.obtener_por_id_sin_activar(user_id_db)
            usuario = self.auth_user_repository.activar(usuario)

        except TokenInvalido:
            raise VerificacionInvalida()
        
        tokens = self.token_service.create_user_tokens(usuario.id_usuario)
        self.cookies_service.set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
        
        return tokens

