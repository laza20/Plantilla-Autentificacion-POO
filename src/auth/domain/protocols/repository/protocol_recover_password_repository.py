from typing import Protocol, runtime_checkable
from datetime import datetime
from src.auth.domain.entities.entitie_recover_password import RecoverPassword

@runtime_checkable
class RecuperarContraseñaProtocol(Protocol):
    """
    Contrato de persistencia de los tokens de recuperación de contraseña.

    Lo consumen los casos de uso de recuperación de contraseña. Cada registro
    asocia un usuario con el hash de un token de un solo uso y su vencimiento.
    La implementación concreta vive fuera del dominio y se arma en la composition
    root (src/container/auth/providers.py).

    No se asume commit al retornar: la confirmación de la transacción no es
    responsabilidad de estos métodos.
    """

    def insertar_recuperacion_contraseña(
            self,
            id_usuario:int, 
            token_hash:str,
            expira_en:datetime )->bool:
        """
        Registra un token de recuperación para un usuario.

        El registro queda sin usar. No invalida los tokens previos del usuario:
        para eso existe invalidar_tokens_anteriores.

        Args:
            id_usuario: ID del usuario que pidió la recuperación.
            token_hash: Hash del token enviado al usuario (nunca el token en claro).
            expira_en: Fecha límite hasta la cual el token puede usarse.

        Returns:
            True si el registro quedó agregado.
        """
        ...



    def verificar_token(
            self,
            tiempo_actual:datetime,
            token_hash:str
    )-> RecoverPassword | bool :
        """
        Valida un token de recuperación a partir de su hash.

        El token es válido si existe un registro con ese token_hash, no fue
        usado y no venció (expira_en >= tiempo_actual).

        Args:
            tiempo_actual: Instante contra el cual se evalúa el vencimiento.
            token_hash: Hash del token recibido.

        Returns:
            El registro RecoverPassword si el token es válido. False en
            cualquier otro caso (no existe, ya usado, sin fecha de vencimiento
            o vencido). No levanta excepciones ni distingue el motivo.
        """
        ...


    def invalidar_tokens_anteriores(self, id_usuario:int)->bool:
        """
        Marca como usados todos los tokens pendientes de un usuario.

        Se usa al emitir un token nuevo, para que solo el último sea válido.
        Los tokens ya usados no se tocan.

        Args:
            id_usuario: ID del usuario cuyos tokens se invalidan.

        Returns:
            True si invalidó al menos un token; False si no había ninguno
            pendiente.
        """
        ...

    def desactivar_token_utilizado(self, id_usuario: int)->bool:
        """
        Marca como usados los tokens pendientes del usuario tras consumir el de recuperación.

        Tiene el mismo efecto que invalidar_tokens_anteriores y existe para
        nombrar el paso final del flujo. Opera sobre todos los tokens
        pendientes del usuario, no sobre uno puntual.

        Args:
            id_usuario: ID del usuario cuyos tokens se invalidan.

        Returns:
            True si invalidó al menos un token; False si no había ninguno
            pendiente.
        """
        ...