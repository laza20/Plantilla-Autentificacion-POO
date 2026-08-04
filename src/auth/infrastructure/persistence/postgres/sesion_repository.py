from src.auth.infrastructure.persistence.postgres.models_sesiones import Sesiones
from sqlalchemy.orm import Session


class SesionRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar_sesion(
        self,
        hash_token: str,
        id_usuario: int,
        ip: str,
        user_agent: str):
        """
        Función para insertar un registro en la base de datos y retornar la sesión actualizada.
        """
        sesion = Sesiones(
            hash_refresh_token=hash_token,
            id_usuario=id_usuario,
            ip=ip,
            user_agent=user_agent
        )
        self.session.add(sesion)
        self.session.commit()
        self.session.refresh(sesion)
        return sesion