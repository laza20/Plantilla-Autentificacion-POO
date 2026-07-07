from fastapi import UploadFile
from src.auth.infrastructure.persistence.postgres.models import AuthUser

class StubImageService:
    def __init__(self):
        pass

    def insertar_imagen(self, objeto_usuario: AuthUser, imagen: UploadFile, servicio="usuarios") -> AuthUser:
        """
        Función para simular la inserción de una imagen.
        """
        # Simula la inserción de la imagen y retorna un nombre de archivo ficticio
        objeto_usuario.imagen = f"{servicio}_imagen_ficticia.jpg"
        return objeto_usuario