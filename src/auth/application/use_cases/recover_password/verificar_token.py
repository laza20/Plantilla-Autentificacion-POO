from src.auth.domain.protocols.protocol_recover_password_repository import RecuperarContraseñaProtocol
from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from datetime import datetime, timezone
from src.auth.domain.exceptions.tokens import TokenNoVerificado



class VerificarTokenUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        token_service: TokenProtocol
        ):
        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.token_service = token_service



    def ejecutar(self, token:str):
        fecha_actual = datetime.now(timezone.utc) 
        token_hasheado = self.token_service.hash_token(token)

        token_verificado = self.recuperar_contraseña_repository.verificar_token(
            fecha_actual, token_hasheado
            )

        if not token_verificado:
            raise TokenNoVerificado()

        nuevo_token = self.token_service.create_reset_token(token_verificado.id_usuario)

        return nuevo_token