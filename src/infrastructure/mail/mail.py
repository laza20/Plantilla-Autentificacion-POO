from jinja2 import Environment, FileSystemLoader
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from src.config.config import Settings, get_settings
from fastapi import Depends

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(
    os.path.dirname(CURRENT_DIR),
    "templates"
)

class MailService:
    def __init__(
        self,
        settings: Settings
    ):
        self.settings = settings
        self.cfg = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
        )
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.fast_mail = FastMail(self.cfg)

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        template = self.env.get_template("verificacion.html")
        
        cuerpo_html = template.render(
            url_verificacion=url,
            nombre_app=nombre_proyecto
        )
        
        return cuerpo_html

    async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto:str)-> None:
        """
        asunto debe contener el asunto por el que se envia el mail, por ejemplo
        activar mail
        """
        message = self._formar_mensaje(email_destino, cuerpo_html, asunto)
        await self.fast_mail.send_message(message)


    def _formar_mensaje(self, email_destino: str, cuerpo_html: str, asunto:str) -> MessageSchema:
        return MessageSchema(
            subject=f"{asunto} - {self.settings.NOMBRE_APP}",
            recipients=[email_destino],
            body=cuerpo_html,
            subtype="html"
        )
        

def get_mail_service(settings: Settings = Depends(get_settings)) -> MailService:
    return MailService(settings=settings)