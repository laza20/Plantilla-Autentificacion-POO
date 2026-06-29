from src.exceptions.domain import SinCargas
from fastapi import UploadFile
import logging
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.models import AuthUser, UserRegisterDTO
from pydantic import ValidationError
from src.exceptions.domain import LongitudExcedida
from src.auth.security.security import Settings


logger = logging.getLogger(__name__)

class RegisterUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordProtocol,
        mail_service: MailProtocol,
        image_service: ImageProtocol,
        token_service: TokenProtocol,
        password_policy : PasswordPolicyService,
        settings : Settings
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.mail_service = mail_service
        self.image_service = image_service
        self.token_service = token_service
        self.password_policy = password_policy
        self.settings = settings

    async def register(self, usuario:UserRegisterDTO, imagen:UploadFile | None) -> AuthUser:
        if usuario is None:
            raise SinCargas()
        
        objeto_usuario = self._normalizar_registro_a_cargar(usuario)
        self.password_policy.validar(objeto_usuario.password)

        objeto_usuario.password = self.password_service.hash_password(objeto_usuario.password)

        if imagen is not None:
            objeto_usuario = self.image_service.insertar_imagen(objeto_usuario, imagen, servicio="usuarios")

        usuario_creado = self.user_repository.insertar(objeto_usuario)

        token_verificacion = self.token_service.create_access_token(str(usuario_creado.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario_creado.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )   

        return usuario_creado


    def _normalizar_registro_a_cargar(self, usuario: UserRegisterDTO) -> AuthUser:
        """
        Funcion encargada de normalizar los datos del usuario antes de ser insertados en la base de datos.
        - Datos limpios debe utilizarse para los datos str con una longitud maxima definida.
        - Valida que la imagen no exceda el tamaño máximo permitido.
        """
        try:

            datos_limpios = {"email": usuario.email.strip().lower(),
                             "password":usuario.password}
            usuario_orm = AuthUser(**datos_limpios)
            
            return usuario_orm

        except ValidationError as e:
            error_detalle = e.errors()[0]
            campo_afectado = error_detalle.get("loc", ["campo"])[0]
            
            if error_detalle.get("type") == "string_too_long":
                raise LongitudExcedida(
                    message=f"El campo '{campo_afectado}' excede el tamaño máximo permitido."
                )
            raise e
        
    def _generar_correo_verificacion(self, token: str) -> str:
        url = (
            f"{self.settings.BASE_URL}/"
            f"{self.settings.NOMBRE_APP}/usuarios/verificar/{token}"
        )

        return self.mail_service.generar_correo_verificacion(
            url=url,
            nombre_proyecto=self.settings.NOMBRE_APP,
        )

