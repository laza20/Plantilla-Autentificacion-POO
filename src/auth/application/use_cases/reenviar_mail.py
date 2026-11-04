from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.shared.protocols.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.auth.infrastructure.mail.auth_mail_content import AuthMailContent

class ReenviarMailUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        mail_content: AuthMailContent,
        token_service: TokenProtocol,
        mail_policy : MailPolicyService,
        base_de_datos_url: str,
        nombre_app:str
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.mail_content = mail_content
        self.token_service = token_service
        self.mail_policy = mail_policy
        self.base_de_datos_url = base_de_datos_url
        self.nombre_app = nombre_app

    async def ejecutar(self, mail_usuario:str) -> dict:
        self.mail_policy.validar(mail_usuario)
        user = self.auth_user_repository.obtener_por_email_sin_activar(mail_usuario)
        if not user:
            raise UsuarioNoEncontrado(f"No se pudo procesar la solicitud para el mail {mail_usuario}")

        token_verificacion = self.token_service.create_verificacion_token(str(user.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=mail_usuario,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )   

        return {"message": "Correo enviado correctamente"}

        
    def _generar_correo_verificacion(self, token: str) -> str:
        url = (
            f"{self.base_de_datos_url}/"
            f"{self.nombre_app}/usuarios/verificar/{token}"
        )

        return self.mail_content.generar_correo_verificacion(
            url=url,
            nombre_proyecto=self.nombre_app,
        )



