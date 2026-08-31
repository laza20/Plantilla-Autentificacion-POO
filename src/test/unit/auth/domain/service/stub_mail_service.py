class StubMailService:
    def __init__(self):
        self.fue_llamado = False
        self.destinatario = None
        self.asunto = None
        self.cuerpo_html = None

    async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto: str) -> None:
        """
        Función para simular el envío de un correo electrónico.
        """
        self.fue_llamado = True
        self.destinatario = email_destino
        self.asunto = asunto
        self.cuerpo_html = cuerpo_html

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Función para simular la generación de un correo de verificación.
        """
        return url

    def generar_correo_recuperacion(self, url: str, nombre_proyecto: str) -> str: 
        return url