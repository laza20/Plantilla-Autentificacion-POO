from auth_core.auth.domain.entities.entitie_recover_password import RecoverPassword
from auth_core.auth.infrastructure.persistence.postgres.models.models_recover_password import (
    RecoverPassword as RecoverPasswordSqlModel
)



def a_entidad(model: RecoverPasswordSqlModel) -> RecoverPassword:
    return RecoverPassword(
        id_recover_password=model.id_recover_password,
        token_hash=model.token_hash,
        expira_en=model.expira_en,
        usado=model.usado,
        id_usuario=model.id_usuario,
    )


def a_modelo(entidad: RecoverPassword) -> RecoverPasswordSqlModel:
    return RecoverPasswordSqlModel(
        id_recover_password=entidad.id_recover_password,
        token_hash=entidad.token_hash,
        expira_en=entidad.expira_en,
        usado=entidad.usado,
        id_usuario=entidad.id_usuario,
    )