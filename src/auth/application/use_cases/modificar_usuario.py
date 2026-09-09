from fastapi import UploadFile
from datetime import date
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.service.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.service.protocol_image_service import ImageProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import (
    AuthUser, AuthUserEmailValidation, UserModifyDTO)
from src.database.enums.estado_entidad import EstadoEntidad
from pydantic import ValidationError
from src.auth.domain.exceptions.domain import LongitudExcedida
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

    async def ejecutar(self, id_usuario:str, usuario:UserModifyDTO, imagen:UploadFile | None) -> AuthUser:
        mail_modificado = False
        copia_usuario = usuario.model_dump()
        objeto_usuario_modificacion = self._normalizar_registro_a_cargar(copia_usuario)

        usuario_db = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        
        if usuario_db is None:
            raise UsuarioNoEncontrado("El usuario no fue encontrado")

        if usuario_db.email != objeto_usuario_modificacion.email and objeto_usuario_modificacion.email is not None:
            mail_modificado = True
            self.mail_policy.validar(objeto_usuario_modificacion.email)
            usuario_db.estado = EstadoEntidad.PENDIENTE

        objeto_modificado = usuario_db.model_copy(update=objeto_usuario_modificacion.model_dump(exclude_none=True))

        if imagen is not None:
            objeto_modificado = self.image_service.insertar_imagen(objeto_modificado, imagen, servicio="usuarios")

        objeto_modificado.updated_at = date.today()
        with self.unit_of_work_service:
            usuario_auth= self.auth_user_repository.modificar_usuario(usuario=objeto_modificado.model_dump())
            if not usuario_auth:
                raise UsuarioNoModificado("El usuario no pudo ser modificado")

        if mail_modificado:
            await self._enviar_mail(objeto_modificado)

        return objeto_modificado

    async def _enviar_mail(self, usuario:AuthUser)->None:
        token_verificacion = self.token_service.create_verificacion_token(str(usuario.id_usuario))
        cuerpo_correo = self._generar_correo_verificacion(token_verificacion)

        await self.mail_service.enviar_mail(
            email_destino=usuario.email,
            cuerpo_html=cuerpo_correo,
            asunto = "Activa tu cuenta"
        )  
            

    def _normalizar_registro_a_cargar(self, usuario: dict) -> AuthUserEmailValidation:
        """
        Funcion encargada de normalizar los datos del usuario antes de ser insertados en la base de datos.
        - Datos limpios debe utilizarse para los datos str con una longitud maxima definida.
        """
        try:
            dict_modificado = usuario.copy()
            for clave, valor in usuario.items():
                if valor is None:
                    continue
                if isinstance(valor, str) and clave == 'email':
                    dict_modificado[clave] = valor.strip().lower()

            usuario_normalizado = AuthUserEmailValidation(**dict_modificado)
            return usuario_normalizado

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

