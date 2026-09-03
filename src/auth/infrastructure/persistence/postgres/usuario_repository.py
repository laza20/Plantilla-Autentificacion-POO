from sqlmodel import Session
from src.auth.infrastructure.persistence.postgres.models_usuario import Usuario

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar(self, usuario:Usuario)-> Usuario:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        self.session.add(usuario)
        return usuario