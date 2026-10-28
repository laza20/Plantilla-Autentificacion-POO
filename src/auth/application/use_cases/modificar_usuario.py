from fastapi import UploadFile
from datetime import date
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.database.protocols.protocol_unit_of_work import UnitOfWorkProtocol
from src.shared.protocols.protocol_mail_service import MailProtocol
from src.shared.protocols.protocol_image_service import ImageProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.infrastructure.persistence.postgres.mappers.mapper_auth_users import a_entidad_usuario_creado
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.domain.entities.entitie_auth_users import (
    EMAIL_MAX_LENGTH,
    AuthUser,
    UserModifyDTO,
)
from src.database.enums.estado_entidad import EstadoEntidad
from src.domain.exceptions.domain import LongitudExcedida
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioNoModificado
from src.auth.infrastructure.security.security import Settings
from src.auth.infrastructure.mail.auth_mail_content import AuthMailContent
from dataclasses import replace


class ModificarUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        mail_content: AuthMailContent,
        image_service: ImageProtocol,
        token_service: TokenProtocol,
        mail_policy : MailPolicyService,
        settings : Settings,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.mail_content = mail_content
        self.image_service = image_service
        self.token_service = token_service
        self.mail_policy = mail_policy
        self.settings = settings
        self.unit_of_work_service = unit_of_work_service

    async def ejecutar(self, id_usuario:int, usuario:UserModifyDTO | None, imagen:UploadFile | None) -> AuthUser:
        mail_modificado = False

        usuario_db = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        if usuario_db is None:
            raise UsuarioNoEncontrado("El usuario no fue encontrado")

        cambios = {}
        if usuario is not None and usuario.email is not None:
            email = self._normalizar_email(usuario.email)

            if usuario_db.email != email:
                self.mail_policy.validar(email)
                cambios["email"] = email
                cambios["estado"] = EstadoEntidad.PENDIENTE
                mail_modificado = True

        objeto_modificado = replace(usuario_db, **cambios)

        if imagen is not None:
            objeto_modificado = self.image_service.insertar_imagen(objeto_modificado, imagen, servicio="usuarios")

        objeto_modificado.updated_at = date.today()
        with self.unit_of_work_service:
            usuario_auth = self.auth_user_repository.modificar_usuario(usuario=objeto_modificado)
            if not usuario_auth:
                raise UsuarioNoModificado("El usuario no pudo ser modificado")

        if mail_modificado:
            await self._enviar_mail(objeto_modificado)

        return a_entidad_usuario_creado(objeto_modificado)

    async def _enviar_mail(self, usuario:AuthUser)->None:
        token_verificacion = self.token_service.create_verificacion_token(str(usuario.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )  
            

    def _normalizar_email(self, email: str) -> str:
        email_normalizado = email.strip().lower()
        if len(email_normalizado) > EMAIL_MAX_LENGTH:
            raise LongitudExcedida(
                message=f"El campo 'email' excede el tamaño máximo permitido."
            )
        return email_normalizado
        
    def _generar_correo_verificacion(self, token: str) -> str:
        url = (
            f"{self.settings.BASE_URL}/"
            f"{self.settings.NOMBRE_APP}/usuarios/verificar/{token}"
        )

        return self.mail_content.generar_correo_verificacion(
            url=url,
            nombre_proyecto=self.settings.NOMBRE_APP,
        )
