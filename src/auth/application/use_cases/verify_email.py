from src.auth.infrastructure.persistence.postgres.models.models_auth_users import UserTokens
import logging
from src.auth.domain.protocols.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.exceptions.tokens import TokenInvalido, VerificacionInvalida
from src.auth.domain.protocols.protocol_token_service import TokenProtocol

logger = logging.getLogger(__name__)

class VerifyMailUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.unit_of_work_service = unit_of_work_service

    def ejecutar(self, token: str)-> UserTokens:
        """
        Funcion encargada de verificar el mail del usuario utilizando un token de verificación.
        El token se decodifica para obtener el ID del usuario, luego se busca el usuario en la base de datos y se activa su cuenta.
        Si el token es inválido o el usuario no existe, se lanzan excepciones correspondientes
        """
        try:
            user_id_db = self.token_service.get_user_id_from_access_token(token)
            usuario = self.auth_user_repository.obtener_por_id_sin_activar(user_id_db)
            with self.unit_of_work_service:
                usuario = self.auth_user_repository.activar(usuario)

        except TokenInvalido:
            raise VerificacionInvalida()
        
        return self.token_service.create_user_tokens(usuario.id_usuario)