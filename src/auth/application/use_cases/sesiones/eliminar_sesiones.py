from src.auth.domain.protocols.repository.protocol_sesion_repository import TokenRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol
from typing import Dict


class EliminarSesionesUseCase:
    def __init__(
        self, 
        sesion_repository: TokenRepositoryProtocol,
        unit_of_work_service: UnitOfWorkProtocol
        ):
        self.sesion_repository = sesion_repository
        self.unit_of_work_service = unit_of_work_service

    def ejecutar(self, id_sesion: int, id_usuario: int) -> Dict:
        with self.unit_of_work_service:
            retorno = self.sesion_repository.eliminar_sesion(id_sesion=id_sesion, id_usuario=id_usuario)

        if retorno:
            return {"message": "Sesión eliminada"}

        return {"message": "La sesion que se quiso eliminar, no pudo ser encontrada"}
