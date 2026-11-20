from src.auth_core.auth.domain.entities.entitie_sesiones import Sesion
from src.auth_core.auth.infrastructure.persistence.postgres.models.models_sesiones import Sesiones as SesionesSqlModel

def a_entidad(model: SesionesSqlModel) -> Sesion:
    return Sesion(
        id_sesion=model.id_sesion,
        hash_refresh_token=model.hash_refresh_token,
        id_usuario=model.id_usuario,
        user_agent=model.user_agent,
        ip=model.ip,
        inicio_sesion=model.inicio_sesion
    )


def a_modelo(entity: Sesion) -> SesionesSqlModel:
    return SesionesSqlModel(
        id_sesion=entity.id_sesion,
        hash_refresh_token=entity.hash_refresh_token,
        user_agent=entity.user_agent,
        ip=entity.ip,
        inicio_sesion=entity.inicio_sesion,
        id_usuario=entity.id_usuario,
    )
