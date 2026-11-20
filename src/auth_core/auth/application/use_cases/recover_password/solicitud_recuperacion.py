from src.auth_core.auth.domain.protocols.repository.protocol_recover_password_repository import RecuperarContraseñaProtocol
from src.auth_core.database.protocols.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth_core.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth_core.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth_core.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError
from src.auth_core.shared.protocols.protocol_mail_service import MailProtocol
from datetime import datetime, timezone, timedelta
from src.auth_core.auth.domain.protocols.service.protocol_auth_mail_content import AuthMailContentProtocol


class SolicitudRecuperacionUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service:MailProtocol,
        mail_content: AuthMailContentProtocol,
        token_service: TokenProtocol,
        base_de_datos_url: str,
        nombre_app:str,
        verificar_mail_recuperacion: timedelta
        ):
        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.unit_of_work_service = unit_of_work_service
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.mail_content = mail_content
        self.token_service = token_service
        self.base_de_datos_url = base_de_datos_url
        self.nombre_app = nombre_app
        self.verificar_mail_recuperacion = verificar_mail_recuperacion

    async def ejecutar(self, email):
        usuario_encontrado = self.auth_user_repository.obtener_por_email(email)

        if not usuario_encontrado:
            raise UsuarioNoEncontrado("Usuario no encontrado en la base de datos")

        expira = datetime.now(timezone.utc) + self.verificar_mail_recuperacion

        token_recuperacion = self.token_service.generar_token_plano()
        token_hash = self.token_service.hash_token(token_recuperacion)

        with self.unit_of_work_service:

            self.recuperar_contraseña_repository.invalidar_tokens_anteriores(usuario_encontrado.id_usuario)
            
            usuario_recuperacion = self.recuperar_contraseña_repository.insertar_recuperacion_contraseña(
                id_usuario=usuario_encontrado.id_usuario, 
                token_hash=token_hash,
                expira_en=expira
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
            f"{self.base_de_datos_url}/"
            f"{self.nombre_app}/usuarios/recuperar/password/{token}"
        )

        return self.mail_content.generar_correo_recuperacion(
            url=url,
            nombre_proyecto=self.nombre_app,
        )