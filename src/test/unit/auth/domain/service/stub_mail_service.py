class StubMailService:
    def __init__(self):
        self.urls_list = []

    async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto: str) -> None:
        """
        Función para simular el envío de un correo electrónico.
        """
        self.urls_list.append(cuerpo_html)

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Función para simular la generación de un correo de verificación.
        """
        return url