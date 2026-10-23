from sqlmodel import Session, select, update
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser as AuthUserSqlModel
from src.database.enums.estado_entidad import EstadoEntidad
from src.auth.domain.exceptions.usuarios_exceptions import MailRepetido
from src.auth.infrastructure.persistence.postgres.mappers.mapper_auth_users import a_entidad, a_modelo
from src.auth.domain.entities.entitie_auth_users import AuthUser
from datetime import datetime

class AuthUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insertar(self, usuario:AuthUser)-> AuthUser:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        modelo = a_modelo(usuario)
        existente = self.session.query(AuthUserSqlModel).filter_by(email=modelo.email).first()
        if existente:
            raise MailRepetido()

        self.session.add(modelo)
        self.session.flush()
        return a_entidad(modelo) 

    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        """
        Función para obtener un usuario por su ID.
        """
        statement = select(AuthUserSqlModel).where(AuthUserSqlModel.id_usuario == id_usuario)
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
        statement = select(AuthUserSqlModel).where(
            AuthUserSqlModel.email == email, 
            AuthUserSqlModel.estado == EstadoEntidad.ACTIVO
        )
        result = self.session.exec(statement).first()
        return a_entidad(result) if result else None
        


    def obtener_por_id(self, id_usuario:int) -> AuthUser | None:
        """
        Funcion para buscar un usuario por medio de su id
        """
        statement = select(AuthUserSqlModel).where(
            AuthUserSqlModel.id_usuario == id_usuario, 
            AuthUserSqlModel.estado == EstadoEntidad.ACTIVO
        )
        result = self.session.exec(statement).first()
        return a_entidad(result) if result else None


    def modificar_contraseña(
            self, 
            id_usuario:int, 
            contraseña_nueva:str, 
            fecha_actual:datetime)->bool: 

        
        statement = (
            update(AuthUserSqlModel)
            .where(
                AuthUserSqlModel.id_usuario == id_usuario,
                AuthUserSqlModel.is_verified == True
            )
            .values(updated_at=fecha_actual, password=contraseña_nueva)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0


    def obtener_por_email_sin_activar(self, email: str) -> AuthUser | None:
        """
        Función para buscar un usuario por su correo electrónico o nombre de usuario
        La misma filtra al usuario que no esta activo, sirve para funciones tales como
        obtener un usuario por mail, el cual es necesario para pedir nuevamente el mail
        de verificacion.
        """
        statement = select(AuthUserSqlModel).where(
            AuthUserSqlModel.email == email, 
            AuthUserSqlModel.estado == EstadoEntidad.PENDIENTE
        )
        result = self.session.exec(statement).first()
        return a_entidad(result) if result else None


    def modificar_usuario(self, usuario:dict)-> bool | None: 
        statement = (
            update(AuthUserSqlModel)
            .where(
                AuthUserSqlModel.id_usuario == usuario["id_usuario"]
            )
            .values(**usuario)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0

    def eliminar_usuario(self, usuario:AuthUser)-> bool | None:
        statement = (
            update(AuthUserSqlModel)
            .where(
                AuthUserSqlModel.id_usuario == usuario["id_usuario"]
            )
            .values(**usuario)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0


    def obtener_usuario_eliminado_por_mail(self, mail_usuario:str)->AuthUser | None: 
        statement = select(AuthUserSqlModel).where(
            AuthUserSqlModel.email == mail_usuario, 
            AuthUserSqlModel.estado == EstadoEntidad.ELIMINADO
        )
        return self.session.exec(statement).first()


    def obtener_usuario_eliminado_por_id(self, id_usuario:int)->AuthUser | None:
        statement = select(AuthUser).where(
            AuthUserSqlModel.id_usuario == id_usuario, 
            AuthUserSqlModel.estado == EstadoEntidad.ELIMINADO
        )
        return self.session.exec(statement).first()

    def activar_usuario_eliminado(self, id_usuario:int)-> bool | None:
        statement = (
            update(AuthUserSqlModel)
            .where(
                AuthUserSqlModel.id_usuario == id_usuario,
                AuthUserSqlModel.estado == EstadoEntidad.ELIMINADO
            )
            .values(eliminado_en=None, estado=EstadoEntidad.ACTIVO)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0
    