from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.infrastructure.security.security import Settings

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
            raise UsuarioNoEncontrado("Usuario no encontrado")
        
    def get_user(self, current_user:AuthUser)-> AuthUser:
        return self.user_repository.obtener_por_id(current_user.id_usuario)


