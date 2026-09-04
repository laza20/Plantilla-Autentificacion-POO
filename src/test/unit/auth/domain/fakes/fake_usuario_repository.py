from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario
from typing import Dict


class FakeUsuarioRepository:
    def __init__(self):
        self._usuarios: Dict[str, Usuario] = {}
        self.fue_llamado: bool = False

    def insertar(
        self,
        usuario:Usuario)->Usuario:
        """
        Función para insertar un registro en la base de datos y retornar el usuario actualizado.
        """
        copia_usuario = usuario.model_copy()
        self._usuarios[usuario.id_usuario] = copia_usuario
        self.fue_llamado = True
        return copia_usuario