from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.database.enums.estado_entidad import EstadoEntidad


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar(self, usuario:AuthUser)-> AuthUser:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        try:
            self.session.add(usuario)
            self.session.commit()
            self.session.refresh(usuario)
            return usuario
        
        except IntegrityError:
            self.session.rollback()
            raise

    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        """
        Función para obtener un usuario por su ID.
        """
        statement = select(AuthUser).where(AuthUser.id_usuario == id_usuario)
        return self.session.exec(statement).first()

    def activar(self, usuario: AuthUser) -> AuthUser:
        """
        Activa un usuario y marca su correo como verificado.
        """
        usuario.estado = EstadoEntidad.ACTIVO
        usuario.is_verified = True

        self.session.commit()
        self.session.refresh(usuario)

        return usuario

    def obtener_por_email(self, email: str) -> AuthUser | None:
        """
        Función para buscar un usuario por su correo electrónico o nombre de usuario.
        """
        statement = select(AuthUser).where(
            AuthUser.email == email, 
            AuthUser.estado == EstadoEntidad.ACTIVO
        )
        return self.session.exec(statement).first()
        


    def obtener_por_id(self, id_usuario:int) -> AuthUser | None:
        """
        Funcion para buscar un usuario por medio de su id
        """
        statement = select(AuthUser).where(
            AuthUser.id_usuario == id_usuario, 
            AuthUser.estado == EstadoEntidad.ACTIVO
        )
        return self.session.exec(statement).first()


