from src.auth.infrastructure.persistence.postgres.models.models_sesiones import Sesiones
from typing import Dict


class FakeSesionRepository:
    def __init__(self):
        self._sesiones: Dict[str, Sesiones] = {}
        self.fue_llamado: bool = False
        self.hash_refresh_token: str = ""
        self.token_eliminado: str = ""
        self._next_sesion_id = 1

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
        copia_sesion.id_sesion = self._next_sesion_id
        self._sesiones[hash_token] = copia_sesion
        self._next_sesion_id += 1
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


    def listar_sesiones(self, id_usuario: int):
        """
        Función para listar todas las sesiones de un usuario.
        """
        self.fue_llamado = True
        sesiones_usuario = [
            sesion for sesion in self._sesiones.values() if sesion.id_usuario == id_usuario
        ]
        return sesiones_usuario

    def eliminar_sesion(self, id_sesion: int, id_usuario: int):
        """
        Función para eliminar una sesión específica de un usuario.
        """
        self.fue_llamado = True
        for hash_refresh_token, sesion in list(self._sesiones.items()):
            if sesion.id_sesion == id_sesion and sesion.id_usuario == id_usuario:
                del self._sesiones[hash_refresh_token]
                self.token_eliminado = hash_refresh_token
                return True

            
        self.token_eliminado = None
        return False