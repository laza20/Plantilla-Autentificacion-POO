from src.auth.infrastructure.persistence.postgres.models_recover_password import RecoverPassword
from sqlalchemy.orm import Session
from sqlmodel import update
from datetime import datetime


class RecoverPasswordRepository:
    def __init__(self, session: Session):
        self.session = session


    def invalidar_tokens_anteriores(self, id_usuario: int) -> None:
        statement = (
            update(RecoverPassword)
            .where(
                RecoverPassword.id_usuario == id_usuario,
                RecoverPassword.usado == False
            )
            .values(usado=True)
        )

        self.session.exec(statement)

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


        
