from src.auth.infrastructure.persistence.postgres.models.models_sesiones import Sesiones
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
        return sesion


    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:
        """
        Función para eliminar una sesión de la base de datos utilizando el hash del refresh token.
        """
        sesion = self.session.query(Sesiones).filter_by(hash_refresh_token=hash_token).first()
        if sesion:
            self.session.delete(sesion)

    def listar_sesiones(
        self,
        id_usuario: int
    ) -> list[Sesiones]:
        """
        Función para listar todas las sesiones activas de un usuario específico.
        """
        return self.session.query(Sesiones).filter_by(id_usuario=id_usuario).all()


    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None:
        """
        Función para eliminar una sesión específica de un usuario.
        """
        sesion = self.session.query(Sesiones).filter_by(id_sesion=id_sesion, id_usuario=id_usuario).first()
        if sesion:
            self.session.delete(sesion)
            return True

        return False