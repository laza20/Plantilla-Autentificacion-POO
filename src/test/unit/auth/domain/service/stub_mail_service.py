class StubMailService:
    def __init__(self):
        pass

    async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto: str) -> None:
        """
        Función para simular el envío de un correo electrónico.
        """
        pass

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Función para simular la generación de un correo de verificación.
        """
        return "correo-generado"