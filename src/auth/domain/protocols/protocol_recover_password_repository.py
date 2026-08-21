from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class RecuperarContraseñaProtocol(Protocol):
    def modificar_contraseña(
            self, 
            id_usuario:int, 
            nueva_contraseña:str, 
            fecha_actual:datetime)->bool: pass

    def desactivar_token_utilizado(self, token_hash:str)->bool:pass

    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str, 
            fecha_expiracion:datetime )->bool:pass

    def insertar_history_password(
            self, 
            id_usuario:int, 
            password_hash_anterior:str, 
            fecha_cambio:datetime)->bool:pass

    def verificar_token(
            self,
            id_usuario:int,
            expira_en:datetime,
            token_hash:str
    )->bool:pass