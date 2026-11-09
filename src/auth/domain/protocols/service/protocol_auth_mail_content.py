from typing import Protocol

class AuthMailContentProtocol(Protocol):

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        ...

    def generar_correo_recuperacion(self, url: str, nombre_proyecto: str) -> str:
        ...

    def generar_correo_eliminacion(self, url: str, nombre_proyecto: str) -> str:
        ...

    def generar_correo_reactivacion(self, url: str, nombre_proyecto: str) -> str:
        ...
