from jinja2 import Environment, FileSystemLoader
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from src.config.config import settings
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generar_correo_verificacion(url: str, nombre_proyecto: str) -> str:
    template = env.get_template("verificacion.html")
    
    cuerpo_html = template.render(
        url_verificacion=url,
        nombre_app=nombre_proyecto
    )
    
    return cuerpo_html

async def enviar_mail(email_destino: str, cuerpo_html: str):
    message = MessageSchema(
        subject="Activa tu cuenta - BookTrace",
        recipients=[email_destino],
        body=cuerpo_html,
        subtype="html"
    )
    cfg = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_TLS=True,
        MAIL_SSL=False
    )
    fm = FastMail(cfg)
    await fm.send_message(message)