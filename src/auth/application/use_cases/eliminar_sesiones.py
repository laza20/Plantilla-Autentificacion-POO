from src.auth.domain.protocols.token_repository import TokenRepositoryProtocol


class EliminarSesionesUseCase:
    def __init__(self, token_repository: TokenRepositoryProtocol):
        self.token_repository = token_repository

    def ejecutar(self, id_sesion: int, id_usuario: int):
        self.token_repository.eliminar_sesion(id_sesion=id_sesion, id_usuario=id_usuario)

