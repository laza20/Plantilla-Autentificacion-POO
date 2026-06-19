from src.auth.models import AuthUser, UserRegisterDTO, LoginResponse, UserTokens
from src.exceptions.domain import SinCargas
from src.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError, LoginError
from src.exceptions.domain import DomainError
from src.auth.repository import UserRepository, get_user_repository
from fastapi import Depends
from src.auth.tokens.tokens import get_token_service, TokenService
from src.auth.security.security import PasswordService, get_password_service
from src.config.config import Settings, get_settings
from src.utils.mail import MailService, get_mail_service
import logging
from src.cloudinary.cloudinary import ImageService, get_image_service
from src.auth.utils.usuarios_utils import UserMapper, get_user_mapper


logger = logging.getLogger(__name__)

class AuthService:
    def __init__(
        self,
        token_service: TokenService,
        user_repository: UserRepository,
        password_service: PasswordService,
        settings: Settings,
        mail_service: MailService,
        image_service: ImageService,
        user_mapper: UserMapper
    ):
        self.token_service = token_service
        self.user_repository = user_repository
        self.password_service = password_service
        self.settings = settings
        self.mail_service = mail_service
        self.image_service = image_service
        self.user_mapper = user_mapper

    async def register(self, usuario:UserRegisterDTO) -> None:
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

    def verificar_mail(self, token: str)-> UserTokens:
        """
        Funcion encargada de verificar el mail del usuario utilizando un token de verificación.
        El token se decodifica para obtener el ID del usuario, luego se busca el usuario en la base de datos y se activa su cuenta.
        Si el token es inválido o el usuario no existe, se lanzan excepciones correspondientes
        """
        try:
            user_id_db = self.token_service.get_user_id_from_access_token(token)
            usuario = self.user_repository.obtener_por_id_sin_activar(user_id_db)
            usuario = self.user_repository.activar(usuario)
            
        except UsuarioNoEncontrado:
            raise UsuarioNoEncontrado("El usuario asociado a este token no existe")
        
        tokens = self._crear_tokens_usuario(usuario.id_usuario)
        
        return tokens



    def login_with_credentials(self, mail: str, password: str)-> LoginResponse:
        try:
            usuario_db = self.user_repository.obtener_por_email(mail)
                
            if not self.password_service.verify_password(password, usuario_db.password):
                raise LoginError("Usuario o contraseña incorrectos")

            return self._emitir_tokens_usuario(usuario_db)
        
        except (UsuarioError, DomainError):
            raise
        except Exception as e:
            logger.exception("Error crítico en service")
            raise UsuarioError("Error al inicial sesion") from e
        

    def get_user(self, current_user:AuthUser)-> AuthUser:
        return self.user_repository.obtener_por_id(current_user.id_usuario)


    def refreshed_token(self, refresh_token: str)-> UserTokens:
        """
        Servicio para refrescar el access token usando un refresh token válido.
        """
        user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)

        new_access_token = self.token_service.create_access_token(user_id)

        return UserTokens(
            access_token=new_access_token,
            refresh_token=refresh_token
        )
        
        
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



def get_auth_service(
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service),
    settings: Settings = Depends(get_settings),
    mail_service: MailService = Depends(get_mail_service),
    image_service: ImageService = Depends(get_image_service),
    user_mapper: UserMapper = Depends(get_user_mapper)
):
    return AuthService(
        token_service,
        user_repository,
        password_service,
        settings,
        mail_service,
        image_service,
        user_mapper
    )