from src.auth.infrastructure.persistence.postgres.models.models_recover_password import RecoverPassword
from sqlalchemy.orm import Session
from sqlmodel import update, select
from datetime import datetime


class RecoverPasswordRepository:
    def __init__(self, session: Session):
        self.session = session


    def invalidar_tokens_anteriores(self, id_usuario: int) -> bool:
        statement = (
            update(RecoverPassword)
            .where(
                RecoverPassword.id_usuario == id_usuario,
                RecoverPassword.usado == False
            )
            .values(usado=True)
        )

        resultado = self.session.exec(statement)
        return resultado.rowcount > 0

    
    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str,
            fecha_expiracion:datetime )->bool:

        recover_password = RecoverPassword(
            id_usuario=id_usuario,
            token_hash=token_hash,
            fecha_expiracion=fecha_expiracion
        )
        self.session.add(recover_password)
        return True


    def verificar_token(
            self,
            tiempo_actual:datetime,
            token_hash:str)->RecoverPassword | bool:

        statement = select(RecoverPassword).where(
            RecoverPassword.token_hash == token_hash,
            RecoverPassword.usado == False
        )

        recover_password = self.session.exec(statement).first()

        if recover_password is None:
            return False

        if recover_password.expira_en >= tiempo_actual:
            return False

        return recover_password

    def desactivar_token_utilizado(self, id_usuario: int)->bool:
        resultado = self.invalidar_tokens_anteriores(id_usuario=id_usuario)
        return resultado