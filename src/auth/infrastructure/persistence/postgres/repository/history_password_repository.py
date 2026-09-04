from src.auth.infrastructure.persistence.postgres.models.models_history_password import HistoryPassword
from sqlalchemy.orm import Session
from datetime import datetime


class HistoryPasswordRepository:
    def __init__(self, session: Session):
        self.session = session


    def insertar_history_repository(
        self, 
        id_usuario:int, 
        password_hash_anterior:str, 
        fecha_cambio:datetime)->bool:

        history_password = HistoryPassword(
            id_usuario=id_usuario,
            fecha_cambio=fecha_cambio,
            password_hash_anterior=password_hash_anterior
        )
        self.session.add(history_password)
        return True