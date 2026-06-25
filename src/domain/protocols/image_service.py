from typing import Protocol, runtime_checkable
from src.auth.models import AuthUser

@runtime_checkable
class ImageProtocol(Protocol):

    def insertar_imagen(self, objeto: AuthUser, servicio:str)-> AuthUser:
        ...
