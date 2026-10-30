from src.auth.domain.protocols.repository.protocol_sesion_repository import TokenRepositoryProtocol
from src.auth.domain.entities.entitie_sesiones import ListaSesiones, SesionVisual, Sesion
from src.auth.infrastructure.persistence.postgres.mappers.mapper_sesiones import a_entidad_no_table

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
        sesiones_visuales = [a_entidad_no_table(s, es_actual=(s.ip == ip)) for s in sesiones]
        return ListaSesiones(sesiones=sesiones_visuales)
