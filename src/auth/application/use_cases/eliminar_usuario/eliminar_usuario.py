from fastapi import UploadFile
from src.auth.domain.protocols.repository.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.repository.protocol_unit_of_work import UnitOfWorkProtocol
from src.auth.domain.protocols.service.protocol_token_service import TokenProtocol
from src.auth.domain.exceptions.domain import ErrorEliminacion
from src.database.enums.estado_entidad import EstadoEntidad
from src.auth.domain.protocols.repository.protocol_sesion_repository import TokenRepositoryProtocol
from datetime import date




class EliminarUsuarioUseCase:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.unit_of_work_service = unit_of_work_service
        self.sesion_repository = sesion_repository

    def ejecutar(self, token_hash:str) -> dict:
        """
        La eliminacion no representa un delete de la base de datos, sino un soft delete dentro de la tabla auth user
        es decir, cambia el estado de un usuario a eliminado. (esto representa a un usuario eliminado para el sistema).
        """
        usuario_id = self.token_service.get_user_id_from_eliminacion_token(token_hash)

        usuario_db = self.auth_user_repository.obtener_por_id(usuario_id)
        usuario_db_copia = usuario_db.model_copy()
        usuario_db_copia.updated_at = date.today()
        usuario_db_copia.estado = EstadoEntidad.ELIMINADO

        with self.unit_of_work_service:
            resultado_eliminacion = self.auth_user_repository.eliminar_usuario(usuario_db_copia.model_dump())
            self.sesion_repository.eliminar_todas_las_sesiones_de_un_usuario(id_usuario=usuario_db_copia.id_usuario)
            if not resultado_eliminacion:
                self._mostrar_errores()

        return {"message":"Usuario eliminado correctamente"}


    def _mostrar_errores(self):
        raise ErrorEliminacion("Error al eliminar el usuario en la base de datos.")


