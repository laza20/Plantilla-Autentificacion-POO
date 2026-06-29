from src.auth.models import AuthUser, UserRegisterDTO, LoginResponse, UserTokens
from src.exceptions.domain import SinCargas
from src.exceptions.usuarios_exceptions import UsuarioError, LoginError
from src.exceptions.tokens import TokenExpirado, TokenInvalido, VerificacionInvalida, VerificacionExpirada
from src.auth.domain.services.password_policy import PasswordPolicyService
from fastapi import Response
import logging
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.security.security import Settings
from src.auth.cookies.cookies import CookiesService



logger = logging.getLogger(__name__)

class AuthService:
    def __init__(
        self,
        token_service: TokenProtocol,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordProtocol,
        settings: Settings,
        mail_service: MailProtocol,
        image_service: ImageProtocol,
        cookies: CookiesService,
        password_policy : PasswordPolicyService,
    ):
        self.token_service = token_service
        self.user_repository = user_repository
        self.password_service = password_service
        self.settings = settings
        self.mail_service = mail_service
        self.image_service = image_service
        self.cookies = cookies
        self.password_policy = password_policy 


    def verificar_mail(self, token: str, response:Response)-> UserTokens:
        """
        Funcion encargada de verificar el mail del usuario utilizando un token de verificación.
        El token se decodifica para obtener el ID del usuario, luego se busca el usuario en la base de datos y se activa su cuenta.
        Si el token es inválido o el usuario no existe, se lanzan excepciones correspondientes
        """
        try:
            user_id_db = self.token_service.get_user_id_from_access_token(token)
            usuario = self.user_repository.obtener_por_id_sin_activar(user_id_db)
            usuario = self.user_repository.activar(usuario)
            
        except TokenExpirado:
            raise VerificacionExpirada()

        except TokenInvalido:
            raise VerificacionInvalida()
        
        tokens = self.token_service.create_user_tokens(usuario.id_usuario)
        self.cookies.set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
        
        return tokens

        

    def get_user(self, current_user:AuthUser)-> AuthUser:
        return self.user_repository.obtener_por_id(current_user.id_usuario)


    def refreshed_token(self, refresh_token: str, response:Response):
        """
        Servicio para refrescar el access token usando un refresh token válido.
        """
        user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)

        new_access_token = self.token_service.create_access_token(user_id)

        self.cookies.set_access_cookie(response, new_access_token)

    def logout(self, response:Response):
        """
        Servicio para deslogear a un usuario.
        """
        self.cookies.delete_auth_cookies(response)

        
    


