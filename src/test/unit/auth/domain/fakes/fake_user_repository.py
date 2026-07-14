from src.auth.domain.exceptions.domain import MailRepetido
from typing import Dict
from src.auth.infrastructure.persistence.postgres.models import AuthUser


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