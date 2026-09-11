from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.service.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.infrastructure.security.security import Settings
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado

class EnviarMailReactivacionUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        token_service: TokenProtocol,
        mail_policy : MailPolicyService,
        settings : Settings
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.token_service = token_service
        self.mail_policy = mail_policy
        self.settings = settings

    async def ejecutar(self, mail_usuario:str) -> dict:
        self.mail_policy.validar(mail_usuario)
        user = self.auth_user_repository.obtener_usuario_eliminado_por_mail(mail_usuario)
        if not user:
            raise UsuarioNoEncontrado(f"No se pudo procesar la solicitud para el mail {mail_usuario}")

        token_verificacion = self.token_service.create_reactivacion_token(str(user.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=mail_usuario,
            cuerpo_html=cuerpo_correo,
            asunto = "Reactiva tu cuenta"
        )   

        return {"message": "Correo enviado correctamente"}

        
    def _generar_correo_verificacion(self, token: str) -> str:
        url = (
            f"{self.settings.BASE_URL}/"
            f"{self.settings.NOMBRE_APP}/usuarios/reactivar/cuenta/{token}"
        )

        return self.mail_service.generar_correo_reactivacion(
            url=url,
            nombre_proyecto=self.settings.NOMBRE_APP,
        )



