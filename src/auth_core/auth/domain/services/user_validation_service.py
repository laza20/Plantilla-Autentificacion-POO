from auth_core.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from auth_core.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from auth_core.auth.domain.entities.entitie_auth_users import AuthUser

class UserValidationService:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
    ):
        self.auth_user_repository = auth_user_repository

    def obtener_usuario_existente(self, email: str) -> AuthUser:
        usuario = self.auth_user_repository.obtener_por_email(email)

        self.verificacion_usuario(usuario)

        return usuario
    

    def verificacion_usuario(self, usuario:AuthUser)-> None:
        if usuario is None:
            raise UsuarioNoEncontrado("Usuario no encontrado")