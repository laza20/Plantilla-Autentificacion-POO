from fastapi import UploadFile
from src.auth.infrastructure.persistence.postgres.models import AuthUser

class StubImageService:
    def __init__(self):
        self.fue_llamado = False
        self.imagen_recibida = None
        self.servicio_recibido = None

    def insertar_imagen(self, objeto_usuario: AuthUser, imagen: UploadFile, servicio="usuarios") -> AuthUser:
        """
        Función para simular la inserción de una imagen.
        """
        objeto_usuario.imagen_url = f"{servicio}_imagen_ficticia.jpg"
        self.fue_llamado = True
        self.imagen_recibida = imagen
        self.servicio_recibido = servicio
        return objeto_usuario