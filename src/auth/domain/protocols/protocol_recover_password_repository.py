from typing import Protocol, runtime_checkable
from datetime import datetime
from src.auth.infrastructure.persistence.postgres.models_recover_password import RecoverPassword

@runtime_checkable
class RecuperarContraseñaProtocol(Protocol):

    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str,
            fecha_expiracion:datetime )->bool:
        """
        Funcion la cual nos permite insertar dentro de la base de datos un registro de tipo recuperacion 
        de contraseña.
        la misma recibe los siguientes parametros como obligatorios para el correcto funcionamiento y armado
        del modelo:
        - id_usuario: permite asignarle a un registro un usuario determinado.
        - token_hash: campo el cual permite la verificacion del token, campo central para el funcionamiento 
        del sistema de recuperacion de controseña.
        - fecha_expiracion: tiempo limite por el cual se puede utilizar el token.
        """
        pass



    def verificar_token(
            self,
            tiempo_actual:datetime,
            token_hash:str
    )-> RecoverPassword | bool :
        """
        Permite verificar que un token recibido existe en la base de datos. Lo parametros recibidos nos permiten:
        - tiempo_actual: Permite verificar que el token sigue siendo valido en tiempo de uso de ejecucion.
        - token_hash: el token para comparar y verificar que el dato llegado es el que se encuentra en la base de
        datos.
        """
        pass


    def invalidar_tokens_anteriores(self, id_usuario:int)->None:pass
    """
    los tokens no utilizado tienen por defecto el campo usado:false, por ende, si se pide un nuevo token
    de recuperacion, los token no utilizados cambian su estado a true
    """