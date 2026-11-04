from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.infrastructure.persistence.postgres.mappers.mapper_auth_users import a_entidad_usuario_creado
from src.auth.domain.entities.entitie_auth_users import AuthUser, UsuarioCreado

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
        
    def get_user(self, current_user:AuthUser)-> UsuarioCreado:
        return a_entidad_usuario_creado(self.auth_user_repository.obtener_por_id(current_user.id_usuario))


