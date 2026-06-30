from src.exceptions.usuarios_exceptions import UsuarioInactivo, UsuarioNoEncontrado
from src.auth.models import AuthUser
from src.exceptions.domain import SinCargas
from fastapi import UploadFile
import logging
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.models import AuthUser, UserRegisterDTO
from pydantic import ValidationError
from src.exceptions.domain import LongitudExcedida
from src.auth.security.security import Settings

class UserValidationService:
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        settings : Settings
    ):
        self.user_repository = user_repository
        self.settings = settings

    def obtener_usuario_existente(self, email: str) -> AuthUser:
        usuario = self.user_repository.obtener_por_email(email)

        self.verificacion_usuario(usuario)

        return usuario
    

    def verificacion_usuario(self, usuario:AuthUser)-> None:
        if usuario is None:
            raise UsuarioNoEncontrado()
        
    def get_user(self, current_user:AuthUser)-> AuthUser:
        return self.user_repository.obtener_por_id(current_user.id_usuario)


