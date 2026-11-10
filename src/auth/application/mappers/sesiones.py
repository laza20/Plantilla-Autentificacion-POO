from src.auth.domain.entities.entitie_sesiones import Sesion
from src.auth.application.dtos.sesiones_dto import SesionVisual


def a_sesion_visual(entity: Sesion, es_actual: bool = False) -> SesionVisual:
    return SesionVisual(
        id_sesion=entity.id_sesion,
        id_usuario=entity.id_usuario,
        user_agent=entity.user_agent,
        ip=entity.ip,
        inicio_sesion=entity.inicio_sesion,
        es_actual=es_actual,
    )
