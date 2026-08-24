from src.auth.domain.protocols.protocol_recover_password_repository import RecuperarContraseñaProtocol
from src.auth.domain.protocols.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError
from src.auth.domain.protocols.protocol_mail_service import MailProtocol
from datetime import datetime, timezone
from src.auth.infrastructure.security.security import Settings


class SolicitudRecuperacionUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service:MailProtocol,
        token_service: TokenProtocol,
        settings: Settings
        ):
        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.unit_of_work_service = unit_of_work_service
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.token_service = token_service
        self.settings = settings


    async def ejecutar(self, email):
        usuario_encontrado = self.auth_user_repository.obtener_por_email(email)

        if not usuario_encontrado:
            raise UsuarioNoEncontrado()

        fecha_actual = datetime.now(timezone.utc)

        token_recuperacion = self.token_service.generar_token_plano()
        token_hash = self.token_service.hash_token(token_recuperacion)

        with self.unit_of_work_service:

            self.recuperar_contraseña_repository.invalidar_tokens_anteriores(usuario_encontrado.id_usuario)

            usuario_recuperacion = self.recuperar_contraseña_repository.insertar_recuperacion_contraseña(
                usuario_encontrado.id_usuario, 
                token_hash,
                fecha_actual
            )

            if not usuario_recuperacion:
                raise UsuarioError("No se pudo registrar la solicitud de recuperación.")


        cuerpo_correo = self._generar_correo_recuperacion(token_recuperacion)
        
        await self.mail_service.enviar_mail(
            email_destino=email,
            cuerpo_html=cuerpo_correo,
            asunto = "Recuperar contraseña"
        )  

        return {"message": "Mail enviado correctamente, revise su bandeja de entrada, si no lo encuentra revise en spam o correos no deseados."}

            

    def _generar_correo_recuperacion(self, token: str) -> str:
        url = (
            f"{self.settings.BASE_URL}/"
            f"{self.settings.NOMBRE_APP}/usuarios/recuperar/password/{token}"
        )

        return self.mail_service.generar_correo_recuperacion(
            url=url,
            nombre_proyecto=self.settings.NOMBRE_APP,
        )