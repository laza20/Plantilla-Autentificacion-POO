from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.service.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.infrastructure.security.security import Settings
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado


class EliminarUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        token_service: TokenProtocol,
        settings : Settings
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.token_service = token_service
        self.settings = settings

    async def ejecutar(self, id_usuario:str):
        usuario = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        if usuario is None:
            raise UsuarioNoEncontrado("No se pudo encontrar el usuario")

        token_eliminacion = self.token_service.create_eliminacion_token(str(usuario.id_usuario))
        cuerpo_correo = self._generar_correo_eliminacion(token_eliminacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Eliminacion de cuenta"
        )   

        return {"message":"Correo de eliminacion enviado a su mail."}


    def _generar_correo_eliminacion(self, token: str) -> str:
        url = (
            f"{self.settings.BASE_URL}/"
            f"{self.settings.NOMBRE_APP}/usuarios/eliminar/cuenta/{token}"
        )

        return self.mail_service.generar_correo_eliminacion(
            url=url,
            nombre_proyecto=self.settings.NOMBRE_APP,
        )
        