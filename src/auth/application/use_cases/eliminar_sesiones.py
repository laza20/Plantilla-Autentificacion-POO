from src.auth.domain.protocols.protocol_sesion_repository import TokenRepositoryProtocol
from typing import Dict


class EliminarSesionesUseCase:
    def __init__(self, sesion_repository: TokenRepositoryProtocol):
        self.sesion_repository = sesion_repository

    def ejecutar(self, id_sesion: int, id_usuario: int) -> Dict:
        retorno = self.sesion_repository.eliminar_sesion(id_sesion=id_sesion, id_usuario=id_usuario)

        if retorno:
            return {"message": "Sesión eliminada"}

        return {"message": "La sesion que se quiso eliminar, no pudo ser encontrada"}
