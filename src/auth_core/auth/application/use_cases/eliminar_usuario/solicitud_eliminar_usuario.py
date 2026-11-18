from auth_core.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from auth_core.shared.protocols.protocol_mail_service import MailProtocol
from auth_core.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from auth_core.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from auth_core.auth.domain.protocols.service.protocol_auth_mail_content import AuthMailContentProtocol


class SolicitudEliminacionUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        mail_content: AuthMailContentProtocol,
        token_service: TokenProtocol,
        base_de_datos_url: str,
        nombre_app:str
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.mail_content = mail_content
        self.token_service = token_service
        self.base_de_datos_url = base_de_datos_url
        self.nombre_app = nombre_app

    async def ejecutar(self, id_usuario:int):
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
            f"{self.base_de_datos_url}/"
            f"{self.nombre_app}/usuarios/eliminar/cuenta/{token}"
        )

        return self.mail_content.generar_correo_eliminacion(
            url=url,
            nombre_proyecto=self.nombre_app,
        )
        