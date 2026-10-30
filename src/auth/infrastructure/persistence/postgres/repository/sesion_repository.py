from src.auth.infrastructure.persistence.postgres.models.models_sesiones import Sesiones as SesionSqlModel
from src.auth.infrastructure.persistence.postgres.mappers.mapper_sesiones import a_entidad, a_modelo
from src.auth.domain.entities.entitie_sesiones import Sesion
from sqlalchemy.orm import Session
from sqlmodel import delete


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
        sesion = SesionSqlModel(
            hash_refresh_token=hash_token,
            id_usuario=id_usuario,
            ip=ip,
            user_agent=user_agent
        )
        self.session.add(sesion)
        self.session.flush()
        return a_entidad(sesion) 


    def eliminar_por_hash(
        self,
        hash_token: str
    ) -> None:
        """
        Función para eliminar una sesión de la base de datos utilizando el hash del refresh token.
        """
        sesion = self.session.query(SesionSqlModel).filter_by(hash_refresh_token=hash_token).first()
        if sesion:
            self.session.delete(sesion)

    def listar_sesiones(
        self,
        id_usuario: int
    ) -> list[Sesion]:
        """
        Función para listar todas las sesiones activas de un usuario específico.
        """
        modelos = self.session.query(SesionSqlModel).filter_by(id_usuario=id_usuario).all()
        return [a_entidad(modelo) for modelo in modelos]


    def eliminar_sesion(
        self,
        id_sesion: int,
        id_usuario: int
    ) -> None:
        """
        Función para eliminar una sesión específica de un usuario.
        """
        sesion = self.session.query(SesionSqlModel).filter_by(id_sesion=id_sesion, id_usuario=id_usuario).first()
        if sesion:
            self.session.delete(sesion)
            return True

        return False


    def eliminar_todas_las_sesiones_de_un_usuario(self, id_usuario:int)->bool: 
        statement = (
            delete(SesionSqlModel)
            .where(SesionSqlModel.id_usuario == id_usuario)
        )

        resultado = self.session.exec(statement)

        return resultado.rowcount > 0