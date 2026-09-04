from src.auth.domain.exceptions.domain import MailRepetido
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioActivo
from typing import Dict
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.database.enums.estado_entidad import EstadoEntidad
from datetime import datetime

class FakeUserRepository:
    def __init__(self):
        self._next_id = 1
        self._users: Dict[str, AuthUser] = {}

    def insertar(self, usuario:AuthUser)-> AuthUser:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        if usuario.email in self._users:
            raise MailRepetido()
        
        copia_usuario = usuario.model_copy()
        copia_usuario.id_usuario = self._next_id
        
        self._users[usuario.email] = copia_usuario
        self._next_id += 1
        return copia_usuario


    def obtener_por_email(self, email: str) -> AuthUser | None:
        """
        Función para buscar un usuario por su correo electrónico o nombre de usuario.
        """
        return self._users.get(email)

    def obtener_por_id(self, id_usuario: int) -> AuthUser | None:
        """
        Función para buscar un usuario por su correo electrónico o nombre de usuario.
        """
        for usuario in self._users.values():
            if usuario.id_usuario == id_usuario:
                return usuario

    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        """
        Funcion para buscar un usuario sin activar, por medio de su id.
        """
        for usuario in self._users.values():
            if usuario.id_usuario == id_usuario:
                if usuario.estado is EstadoEntidad.ACTIVO:
                    raise UsuarioActivo("El usuario que quiere activar, ya se encuentra activo")

                if usuario.is_verified is True:
                    raise UsuarioActivo("El usuario que quiere activar, ya se encuentra activo")

                return usuario

        raise UsuarioNoEncontrado(f"No se encontro al usuario con el id {id_usuario}")

    def activar(self, usuario: AuthUser) -> AuthUser:
        """
        Funcion encargada de activar a un usuario cuando se verifica el mail.
        """
        usuario.estado = EstadoEntidad.ACTIVO
        usuario.is_verified = True
        return usuario

    def modificar_contraseña(self, id_usuario:int, contraseña_nueva:str, fecha_actual:datetime)->bool: 
        usuario = self.obtener_por_id(id_usuario=id_usuario)
        usuario.password = contraseña_nueva
        usuario.updated_at = fecha_actual
        return True

