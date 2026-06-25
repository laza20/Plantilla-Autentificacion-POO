from src.auth.models import AuthUser, UserRegisterDTO, LoginResponse, UserTokens
from src.exceptions.domain import SinCargas
from src.exceptions.usuarios_exceptions import UsuarioError, LoginError
from src.exceptions.tokens import TokenExpirado, TokenInvalido, VerificacionInvalida, VerificacionExpirada
from src.exceptions.domain import DomainError
from fastapi import Response
import logging
from src.domain.protocols.user_repository import UserRepositoryProtocol
from src.domain.protocols.token_service import TokenProtocol
from src.domain.protocols.password_service import PasswordProtocol
from src.domain.protocols.mail_service import MailProtocol
from src.domain.protocols.image_service import ImageProtocol
from src.auth.security.security import Settings
from src.auth.utils.usuarios_utils import UserMapper
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
        user_mapper: UserMapper,
        cookies: CookiesService
    ):
        self.token_service = token_service
        self.user_repository = user_repository
        self.password_service = password_service
        self.settings = settings
        self.mail_service = mail_service
        self.image_service = image_service
        self.user_mapper = user_mapper
        self.cookies = cookies

    async def register(self, usuario:UserRegisterDTO) -> AuthUser:
        if not usuario:
            raise SinCargas()
        
        objeto_usuario = self.user_mapper.orquestador_carga(usuario)
        objeto_usuario.password = self.password_service.hash_password(objeto_usuario.password)

        if objeto_usuario.imagen_url != None:
            objeto_usuario = self.image_service.insertar_imagen(objeto_usuario, servicio="usuarios")

        usuario_creado = self.user_repository.insertar(objeto_usuario)

        token_verificacion = self.token_service.create_access_token(str(usuario_creado.id_usuario))
        cuerpo_correo = self._formar_url_mail(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario_creado.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )   

        return usuario_creado

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
        
        tokens = self._crear_tokens_usuario(usuario.id_usuario)
        self.cookies.set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
        
        return tokens



    def login(self, mail: str, password: str, response:Response)-> LoginResponse:
        try:
            usuario_db = self.user_repository.obtener_por_email(mail)
                
            if not self.password_service.verify_password(password, usuario_db.password):
                raise LoginError("Usuario o contraseña incorrectos")
            
            login_response = self._emitir_tokens_usuario(usuario_db)
            self.cookies.set_auth_cookies(
                response, 
                login_response.tokens.access_token, 
                login_response.tokens.refresh_token
                )
            return login_response
        
        except (UsuarioError, DomainError):
            raise
        except Exception as e:
            logger.exception("Error crítico en service")
            raise UsuarioError("Error al inicial sesion") from e
        

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

        
        
    def _emitir_tokens_usuario(self, usuario:AuthUser)-> LoginResponse:
            
            tokens = self._crear_tokens_usuario(usuario.id_usuario)
            usuario_publico = self.user_mapper.retornar_usuario_publico(usuario)

            return LoginResponse(
                tokens=tokens,
                usuario=usuario_publico
            )
    
    def _formar_url_mail(self, token_verificacion:str)-> str:
        cuerpo_correo = self.mail_service.generar_correo_verificacion(
            url=f"{self.settings.BASE_URL}/{self.settings.NOMBRE_APP}/usuarios/verificar/{token_verificacion}",
            nombre_proyecto=self.settings.NOMBRE_APP
        )
        return cuerpo_correo
    
    def _crear_tokens_usuario(self, user_id:int) -> UserTokens:

        return UserTokens(
            access_token=self.token_service.create_access_token(str(user_id)),
            refresh_token=self.token_service.create_refresh_token(str(user_id))
        )

