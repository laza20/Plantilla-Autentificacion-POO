


class StubAuthMailContent:
    def __init__(self):
        self.fue_llamado = False

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        self.fue_llamado = True
        return url

    def generar_correo_recuperacion(self, url: str, nombre_proyecto: str) -> str:
        self.fue_llamado = True
        return url
    
    def generar_correo_eliminacion(self, url: str, nombre_proyecto: str) -> str:
        self.fue_llamado = True
        return url

    def generar_correo_reactivacion(self, url: str, nombre_proyecto: str) -> str:
        self.fue_llamado = True
        return url
