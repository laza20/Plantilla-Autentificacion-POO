from src.auth.infrastructure.persistence.postgres.models_history_password import HistoryPassword
from datetime import datetime

class FakeHistoryPasswordRepository:
    def __init__(self):
        self.history_password: dict[str, HistoryPassword] = {}
        self.fue_llamado: bool = False
        self._next_history_password_id= 1

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

        history_password.id_history_password = self._next_history_password_id
        copia_history_password = history_password.model_copy()
        self.history_password[id_usuario] = copia_history_password
        self._next_history_password_id += 1
        self.fue_llamado = True
        return True