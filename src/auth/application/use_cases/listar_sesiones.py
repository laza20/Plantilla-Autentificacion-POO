from src.auth.domain.protocols.token_repository import TokenRepositoryProtocol
from src.auth.infrastructure.persistence.postgres.models_sesiones import ListaSesiones, SesionesVisual


class ListarSesionesUseCase:
    def __init__(
            self,
            token_repository: TokenRepositoryProtocol
            ):
        self.token_repository = token_repository

    def ejecutar(self, id_usuario:int, ip:str) -> ListaSesiones:
        sesiones = self.token_repository.listar_sesiones(id_usuario=id_usuario)
        return self._transformar_sesiones(sesiones, ip)

    def _transformar_sesiones(self, sesiones: list[SesionesVisual], ip:str) -> ListaSesiones:
        sesiones_transformadas = [SesionesVisual(**s.dict()) for s in sesiones]
        for s in sesiones_transformadas:
            if s.ip == ip:
                s.es_actual = True
        return ListaSesiones(sesiones=sesiones_transformadas)

