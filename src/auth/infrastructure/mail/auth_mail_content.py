import os
from src.shared.infrastructure.mail.template_renderer import TemplateRenderer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "templates")

class AuthMailContent:
    def __init__(self, renderer: TemplateRenderer):
        self.renderer = renderer

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        return self.renderer.render(
            "verificacion.html", url_verificacion=url, nombre_app=nombre_proyecto
        )

    def generar_correo_recuperacion(self, url: str, nombre_proyecto: str) -> str:
        return self.renderer.render(
            "recuperacion_contraseña.html", url_reset=url, nombre_app=nombre_proyecto
        )

    def generar_correo_eliminacion(self, url: str, nombre_proyecto: str) -> str:
        return self.renderer.render(
           "eliminar_cuenta.html", url_eliminacion=url, nombre_app=nombre_proyecto
        )

    def generar_correo_reactivacion(self, url: str, nombre_proyecto: str) -> str:
        return self.renderer.render(
           "reactivar_cuenta.html", url_reactivacion=url, nombre_app=nombre_proyecto
        )
