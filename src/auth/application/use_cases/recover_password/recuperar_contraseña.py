from src.auth.domain.protocols.protocol_recover_password_repository import RecuperarContraseñaProtocol
from src.auth.domain.protocols.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.protocol_password_service import PasswordProtocol
from src.auth.domain.protocols.protocol_history_password_repository import HistoryRepositoryProtocol
from src.auth.domain.protocols.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.infrastructure.persistence.postgres.models_recover_password import RecoverPassword
from src.auth.domain.services.password_policy import PasswordPolicyService
from datetime import datetime, timezone
from src.auth.domain.exceptions.tokens import TokenNoDesactivado
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoModificado, UsuarioNoEncontrado
from src.auth.domain.exceptions.domain import ErrorCreacion




class RecuperarContraseñaUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        password_service: PasswordProtocol,
        history_contraseña_repository: HistoryRepositoryProtocol,
        password_policy : PasswordPolicyService,
        auth_user_repository: AuthUserRepositoryProtocol
        ):
        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.unit_of_work_service = unit_of_work_service
        self.password_service = password_service
        self.history_contraseña_repository = history_contraseña_repository
        self.password_policy = password_policy
        self.auth_user_repository = auth_user_repository


    def ejecutar(self, id_usuario:int, nueva_contraseña:str)-> dict:

        self.password_policy.validar(nueva_contraseña)
        contraseña_hasheada = self.password_service.hash_password(nueva_contraseña)
        fecha_actual = datetime.now(timezone.utc)
        usuario = self.auth_user_repository.obtener_por_id(id_usuario=id_usuario)
        if not usuario:
            raise UsuarioNoEncontrado()

        with self.unit_of_work_service:
            history_password = self.history_contraseña_repository.insertar_history_repository(
                id_usuario=usuario.id_usuario,
                password_hash_anterior=usuario.password,
                fecha_cambio=fecha_actual
                )
            
            contraseña_modificada = self.auth_user_repository.modificar_contraseña(
                id_usuario=usuario.id_usuario,
                contraseña_nueva=contraseña_hasheada,
                fecha_actual = fecha_actual
                )

            token_desactivado = self.recuperar_contraseña_repository.desactivar_token_utilizado(
                id_usuario=usuario.id_usuario)

            self._mostrar_error(token_desactivado, contraseña_modificada, history_password)


        return {"message": "La contraseña fue modificada correctamente."}

    def _mostrar_error(self, token_desactivado:RecoverPassword | bool, contraseña_modificada:bool, history_password:bool)->None:
            if not token_desactivado:
                raise TokenNoDesactivado()
            if not contraseña_modificada:
                raise UsuarioNoModificado()
            if not history_password:
                raise ErrorCreacion()