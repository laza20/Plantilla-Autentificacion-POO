from sqlmodel import Session, select, update
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.database.enums.estado_entidad import EstadoEntidad
from src.auth.domain.exceptions.domain import MailRepetido
from datetime import datetime

class AuthUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar(self, usuario:AuthUser)-> AuthUser:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        existente = self.session.query(AuthUser).filter_by(email=usuario.email).first()
        if existente:
            raise MailRepetido()

        self.session.add(usuario)
        self.session.flush()
        return usuario

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


    def modificar_contraseña(
            self, 
            id_usuario:int, 
            contraseña_nueva:str, 
            fecha_actual:datetime)->bool: 

        
        statement = (
            update(AuthUser)
            .where(
                AuthUser.id_usuario == id_usuario,
                AuthUser.is_verified == True
            )
            .values(updated_at=fecha_actual, password=contraseña_nueva)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0