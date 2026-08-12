from src.auth.domain.protocols.token_repository import TokenRepositoryProtocol
from typing import Dict


class EliminarSesionesUseCase:
    def __init__(self, token_repository: TokenRepositoryProtocol):
        self.token_repository = token_repository

    def ejecutar(self, id_sesion: int, id_usuario: int) -> Dict:
        retorno = self.token_repository.eliminar_sesion(id_sesion=id_sesion, id_usuario=id_usuario)

        if retorno:
            return {"message": "Sesión eliminada"}

        return {"message": "La sesion que se quiso eliminar, no pudo ser encontrada"}
