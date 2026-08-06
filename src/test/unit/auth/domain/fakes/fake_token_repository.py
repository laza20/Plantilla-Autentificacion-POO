from src.auth.infrastructure.persistence.postgres.models_sesiones import Sesiones
from typing import Dict


class FakeSesionRepository:
    def __init__(self):
        self._sesiones: Dict[str, Sesiones] = {}
        self.fue_llamado: bool = False
        self.hash_refresh_token: str = ""
        self.token_eliminado: str = ""

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
        copia_sesion = sesion.model_copy()
        self._sesiones[hash_token] = copia_sesion
        self.fue_llamado = True
        self.hash_refresh_token = hash_token
        return copia_sesion

    def eliminar_por_hash(self, hash_token: str):
        """
        Función para eliminar un registro en la base de datos por hash.
        """
        if hash_token in self._sesiones:
            del self._sesiones[hash_token]
            self.fue_llamado = True
            self.token_eliminado = hash_token
            return True
        else:
            return False