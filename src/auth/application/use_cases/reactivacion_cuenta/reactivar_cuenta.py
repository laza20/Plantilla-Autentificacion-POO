from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import ErrorCreacion
from src.auth.infrastructure.security.security import Settings
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioNoEliminado, PeriodoReactivacionFinalizado
from src.database.enums.estado_entidad import EstadoEntidad
from datetime import date, timedelta


class ReactivarUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        settings : Settings,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.settings = settings
        self.unit_of_work_service = unit_of_work_service

    def ejecutar(self, token:str) -> AuthUser:

        id_usuario = self.token_service.get_user_id_from_reactivacion_token(token)
        usuario_db = self.auth_user_repository.obtener_usuario_eliminado_por_id(id_usuario)
        if not usuario_db:
            raise UsuarioNoEncontrado("No se ah podido encontrar al usuario que desea reactivar.")

        if usuario_db.estado != EstadoEntidad.ELIMINADO:
            raise UsuarioNoEliminado()

        dia_actual = date.today()
        if usuario_db.eliminado_en + timedelta(minutes=self.settings.REACTIVACION_CUENTA) > dia_actual:
            raise PeriodoReactivacionFinalizado()

        with self.unit_of_work_service:
            resultado = self.auth_user_repository.activar_usuario_eliminado(
                id_usuario=id_usuario
            )
            self._mostrar_errores(resultado=resultado)
            

        return {"message":"La cuenta fue reactivada correctamente."}


    def _mostrar_errores(self, resultado:bool | None):
        if not resultado:
            raise ErrorCreacion("Error al activar el usuario.")
            
 

