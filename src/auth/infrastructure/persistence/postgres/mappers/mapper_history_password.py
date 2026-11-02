from src.auth.domain.entities.entitie_history_password import HistoryPassword
from src.auth.infrastructure.persistence.postgres.models import HistoryPassword as HistoryPasswordSqlModel


def a_entidad(model: HistoryPasswordSqlModel) -> HistoryPassword:
    return HistoryPassword(
        id_history_password=model.id_history_password,
        password_hash_anterior=model.password_hash_anterior,
        fecha_cambio=model.fecha_cambio,
        id_usuario=model.id_usuario,
    )


def a_modelo(entidad: HistoryPassword) -> HistoryPasswordSqlModel:
    return HistoryPasswordSqlModel(
        id_history_password=entidad.id_history_password,
        password_hash_anterior=entidad.password_hash_anterior,
        fecha_cambio=entidad.fecha_cambio,
        id_usuario=entidad.id_usuario,
    )