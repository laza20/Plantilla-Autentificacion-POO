from sqlmodel import Session
from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario as UsuarioSqlModel
from src.auth.infrastructure.persistence.postgres.mappers.mapper_usuario import a_entidad, a_modelo
from src.auth.domain.entities.entitie_usuario import Usuario

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar(self, usuario:Usuario)-> Usuario:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        modelo = a_modelo(usuario)
        self.session.add(modelo)
        return a_entidad(modelo)