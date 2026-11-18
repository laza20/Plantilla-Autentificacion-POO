from auth_core.auth.domain.protocols.repository.protocol_sesion_repository import TokenRepositoryProtocol
from auth_core.auth.domain.entities.entitie_sesiones import Sesion
from auth_core.auth.application.dtos.sesiones_dto import ListaSesiones
from auth_core.auth.application.mappers.sesiones import a_sesion_visual

class ListarSesionesUseCase:
    def __init__(
            self,
            sesion_repository: TokenRepositoryProtocol
            ):
        self.sesion_repository = sesion_repository

    def ejecutar(self, id_usuario:int, ip:str) -> ListaSesiones:
        sesiones = self.sesion_repository.listar_sesiones(id_usuario=id_usuario)
        return self._transformar_sesiones(sesiones, ip)

    def _transformar_sesiones(self, sesiones: list[Sesion], ip: str) -> ListaSesiones:
        sesiones_visuales = [a_sesion_visual(s, es_actual=(s.ip == ip)) for s in sesiones]
        return ListaSesiones(sesiones=sesiones_visuales)
