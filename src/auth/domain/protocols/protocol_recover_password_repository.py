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



    def verificar_token(
            self,
            id_usuario:int,
            expira_en:datetime,
            token_hash:str
    )->bool:pass


    def invalidar_tokens_anteriores(self, id_usuario:int)->None:pass
    """
    los tokens no utilizado tienen por defecto el campo usado:false, por ende, si se pide un nuevo token
    de recuperacion, los token no utilizados cambian su estado a true
    """