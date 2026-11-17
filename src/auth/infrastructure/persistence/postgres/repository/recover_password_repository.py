from src.auth.infrastructure.persistence.postgres.models.models_recover_password import RecoverPassword as RecoverPasswordSqlModel
from src.auth.domain.entities.entitie_recover_password import RecoverPassword
from src.auth.infrastructure.persistence.postgres.mappers.mapper_recover_password import a_entidad
from sqlmodel import update, select, Session, col
from datetime import datetime


class RecoverPasswordRepository:
    def __init__(self, session: Session):
        self.session = session


    def invalidar_tokens_anteriores(self, id_usuario: int) -> bool:
        statement = (
            update(RecoverPasswordSqlModel)
            .where(
                col(RecoverPasswordSqlModel.id_usuario) == id_usuario,
                col(RecoverPasswordSqlModel.usado) == False
            )
            .values(usado=True)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0

    
    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str,
            expira_en:datetime )->bool:

        recover_password = RecoverPasswordSqlModel(
            id_usuario=id_usuario,
            token_hash=token_hash,
            expira_en=expira_en
        )
        self.session.add(recover_password)
        return True


    def verificar_token(
            self,
            tiempo_actual:datetime,
            token_hash:str)->RecoverPassword | bool:

        statement = select(RecoverPasswordSqlModel).where(
            RecoverPasswordSqlModel.token_hash == token_hash,
            RecoverPasswordSqlModel.usado == False
        )

        recover_password = self.session.exec(statement).first()

        if recover_password is None:
            return False

        if recover_password.expira_en is None:
            return False

        if recover_password.expira_en < tiempo_actual:
            return False

        return a_entidad(recover_password)

    def desactivar_token_utilizado(self, id_usuario: int)->bool:
        resultado = self.invalidar_tokens_anteriores(id_usuario=id_usuario)
        return resultado