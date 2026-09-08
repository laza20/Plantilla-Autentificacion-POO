from fastapi import UploadFile
import logging
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.service.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.service.protocol_image_service import ImageProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser, AuthUserEmailValidation, AuthUserNoTable
from src.auth.infrastructure.persistence.postgres.repository.usuario_repository import Usuario
from pydantic import ValidationError
from src.auth.domain.exceptions.domain import LongitudExcedida, SinCargas, ErrorCreacion
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioNoModificado
from src.auth.infrastructure.security.security import Settings



class ModificarUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        image_service: ImageProtocol,
        token_service: TokenProtocol,
        mail_policy : MailPolicyService,
        settings : Settings,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.image_service = image_service
        self.token_service = token_service
        self.mail_policy = mail_policy
        self.settings = settings
        self.unit_of_work_service = unit_of_work_service

    async def ejecutar(self, id_usuario:str, usuario:AuthUser, imagen:UploadFile | None) -> AuthUser:
        mail_modificado = False
        copia_usuario = usuario.model_dump()
        usuario_db = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        objeto_usuario = self._normalizar_registro_a_cargar(copia_usuario)
        
        if usuario_db is None:
            raise UsuarioNoEncontrado("El usuario no fue encontrado")
        usuario_db_copia = usuario_db.model_dump()


        if objeto_usuario["email"] != usuario_db_copia["email"]:
            mail_modificado = True
            self.mail_policy.validar(copia_usuario["email"])

        if imagen is not None:
            copia_usuario = self.image_service.insertar_imagen(copia_usuario, imagen, servicio="usuarios")

        with self.unit_of_work_service:
            objeto_usuario = AuthUser(**copia_usuario)
            usuario_auth= self.auth_user_repository.modificar_usuario(usuario=objeto_usuario)
            if not usuario_auth:
                raise UsuarioNoModificado("El usuario no pudo ser modificado")

        if mail_modificado:
            await self._enviar_mail(usuario_auth)

        return usuario_auth

    async def _enviar_mail(self, usuario:AuthUser)->None:
        token_verificacion = self.token_service.create_verificacion_token(str(usuario.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )  
            

    def _normalizar_registro_a_cargar(self, usuario: dict) -> AuthUser:
        """
        Funcion encargada de normalizar los datos del usuario antes de ser insertados en la base de datos.
        - Datos limpios debe utilizarse para los datos str con una longitud maxima definida.
        - Valida que la imagen no exceda el tamaño máximo permitido.
        """
        try:
            usuario["email"] = usuario["email"].strip().lower()
            AuthUserEmailValidation(
                email=usuario["email"]
            )

            return usuario

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

    def _preparar_usuario_registro(self, usuario:AuthUser)->Usuario:
        """
        Funcion encargada de preparar el objeto Usuario para ser insertado en la base de datos.
        """
        usuario_orm = Usuario(
            **usuario.model_dump()
        )
        return usuario_orm

