from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.repository.protocol_sesion_repository import TokenRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol

class LogoutUseCase:
    def __init__(
        self,
        token_service: TokenProtocol,
        sesion_repository: TokenRepositoryProtocol,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.token_service = token_service
        self.sesion_repository = sesion_repository
        self.unit_of_work_service = unit_of_work_service

    def ejecutar(self, refresh_token: str):
        """
        Servicio para deslogear a un usuario.
        """
        hashed_token = self.token_service.hash_token(refresh_token)
        with self.unit_of_work_service:
            self.sesion_repository.eliminar_por_hash(hashed_token)
