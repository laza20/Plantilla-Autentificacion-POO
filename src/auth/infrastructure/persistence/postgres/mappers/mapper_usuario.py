from src.auth.domain.entities.entitie_usuario import Usuario
from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario as UsuarioSqlModel


def a_entidad(modelo: UsuarioSqlModel) -> Usuario:
    return Usuario(
        id_usuario=modelo.id_usuario
    )


def a_modelo(entidad: Usuario) -> UsuarioSqlModel:
    return UsuarioSqlModel(
        id_usuario=entidad.id_usuario
    )