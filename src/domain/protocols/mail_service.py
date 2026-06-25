from typing import Protocol, runtime_checkable

@runtime_checkable
class MailProtocol(Protocol):

    def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto:str)-> None:
        ...

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        ...
