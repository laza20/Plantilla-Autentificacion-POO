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