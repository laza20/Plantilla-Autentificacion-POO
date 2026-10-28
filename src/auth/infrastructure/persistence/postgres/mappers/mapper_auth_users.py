from src.auth.domain.entities.entitie_auth_users import AuthUser, AuthUserNoTable, UsuarioCreado, AuthUserEmailValidation
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser as AuthUserSqlModel


def a_entidad(modelo: AuthUserSqlModel) -> AuthUser:
    return AuthUser(
        id_usuario=modelo.id_usuario,
        email=modelo.email,
        password=modelo.password,
        imagen_url=modelo.imagen_url,
        imagen_public_id=modelo.imagen_public_id,
        estado=modelo.estado,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
        is_verified=modelo.is_verified,
        eliminado_en=modelo.eliminado_en,
    )


def a_modelo(entidad: AuthUser) -> AuthUserSqlModel:
    return AuthUserSqlModel(
        id_usuario=entidad.id_usuario,
        email=entidad.email,
        password=entidad.password,
        imagen_url=entidad.imagen_url,
        imagen_public_id=entidad.imagen_public_id,
        estado=entidad.estado,
        created_at=entidad.created_at,
        updated_at=entidad.updated_at,
        is_verified=entidad.is_verified,
        eliminado_en=entidad.eliminado_en,
    )


def a_entidad_no_table(modelo: AuthUserSqlModel) -> AuthUserNoTable:
    return AuthUserNoTable(
        email=modelo.email,
        password=modelo.password,
        imagen_url=modelo.imagen_url,
        imagen_public_id=modelo.imagen_public_id,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
        is_verified=modelo.is_verified,
        eliminado_en=modelo.eliminado_en,
    )


def a_modelo_desde_no_table(entidad: AuthUserNoTable) -> AuthUserSqlModel:
    return AuthUserSqlModel(
        email=entidad.email,
        password=entidad.password,
        imagen_url=entidad.imagen_url,
        imagen_public_id=entidad.imagen_public_id,
        created_at=entidad.created_at,
        updated_at=entidad.updated_at,
        is_verified=entidad.is_verified,
        eliminado_en=entidad.eliminado_en,
    )


def a_entidad_usuario_creado(modelo: AuthUserSqlModel) -> UsuarioCreado:
    return UsuarioCreado(
        id_usuario=modelo.id_usuario,
        email=modelo.email,
        imagen_url=modelo.imagen_url,
        created_at=modelo.created_at,
        is_verified=modelo.is_verified
    )


def a_entidad_email_validation(entidad:AuthUserEmailValidation) -> AuthUserSqlModel:
    return UsuarioCreado(
        email=entidad.email
    )
