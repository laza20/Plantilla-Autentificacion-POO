from src.auth_core.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth_core.auth.application.dtos.auth_user_dto import UsuarioCreado


class ObtenerUsuarioActualUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol
    ):
        self.auth_user_repository = auth_user_repository

    def ejecutar(self, id_usuario:int) -> UsuarioCreado:
        usuario_db = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        return UsuarioCreado(
            id_usuario=usuario_db.id_usuario,
            email=usuario_db.email,
            imagen_url=usuario_db.imagen_url,
            is_verified=usuario_db.is_verified
        )



