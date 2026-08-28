from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.protocol_sesion_repository import TokenRepositoryProtocol

class LogoutUseCase:
    def __init__(
        self,
        token_service: TokenProtocol,
        token_repository: TokenRepositoryProtocol
    ):
        self.token_service = token_service
        self.token_repository = token_repository

    def ejecutar(self, refresh_token: str):
        """
        Servicio para deslogear a un usuario.
        """
        hashed_token = self.token_service.hash_token(refresh_token)
        self.token_repository.eliminar_por_hash(hashed_token)
