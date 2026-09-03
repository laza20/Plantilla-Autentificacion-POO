from src.auth.infrastructure.persistence.postgres.models_auth_users import LoginResponse, AuthUser, UsuarioLogeado
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioError, LoginError
from src.auth.domain.exceptions.domain import DomainError
import logging
from src.auth.domain.protocols.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.protocol_password_service import PasswordProtocol
from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.protocol_sesion_repository import TokenRepositoryProtocol
from src.auth.domain.services.user_validation_service import UserValidationService


logger = logging.getLogger(__name__)

class LoginUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        password_service: PasswordProtocol,
        token_service: TokenProtocol,
        user_validation_service: UserValidationService,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.password_service = password_service
        self.token_service = token_service
        self.user_validation_service = user_validation_service
        self.sesion_repository = sesion_repository

    def ejecutar(self, email: str, password: str, ip:str, user_agent:str)-> LoginResponse:
        try:
            usuario_db = self.user_validation_service.obtener_usuario_existente(email)
                
            if not self.password_service.verify_password(password, usuario_db.password):
                raise LoginError("Usuario o contraseña incorrectos")
            
            login_response = self._emitir_tokens_usuario(usuario_db)
            hashed_token = self.token_service.hash_token(login_response.tokens.refresh_token)
            self._insertar_sesion(
                hashed_token=hashed_token,
                id_usuario=usuario_db.id_usuario,
                ip=ip,
                user_agent=user_agent
            )
            return login_response
        
        except (UsuarioError, DomainError):
            raise
        except Exception as e:
            logger.exception("Error crítico en service")
            raise UsuarioError("Error al inicial sesion") from e

    def _emitir_tokens_usuario(self, usuario:AuthUser)-> LoginResponse:
            
            tokens = self.token_service.create_user_tokens(usuario.id_usuario)
            usuario_publico = self._retornar_usuario_publico(usuario)

            return LoginResponse(
                tokens=tokens,
                usuario=usuario_publico
            )

    def _retornar_usuario_publico(self, usuario:AuthUser)-> UsuarioLogeado:
        return UsuarioLogeado(
            email= usuario.email,
            imagen_url= usuario.imagen_url
        )

    def _insertar_sesion(self, hashed_token:str, id_usuario:int, ip:str, user_agent:str):
        self.sesion_repository.insertar_sesion(
            hash_token=hashed_token,
            id_usuario=id_usuario,
            ip=ip,
            user_agent=user_agent
        )
