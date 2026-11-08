from src.auth.domain.entities.entitie_auth_users import AuthUser
from src.auth.application.dtos.auth_user_dto import UsuarioCreado


def a_usuario_creado(entidad: AuthUser) -> UsuarioCreado:
    return UsuarioCreado(
        id_usuario=entidad.id_usuario,
        email=entidad.email,
        imagen_url=entidad.imagen_url,
        created_at=entidad.created_at,
        is_verified=entidad.is_verified,
    )