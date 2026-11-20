from src.auth_core.auth.domain.entities.entitie_auth_users import AuthUser
from src.auth_core.shared.protocols.protocol_imagen_tipado import TipadoImagenProtocol

class StubImageService:
    def __init__(self):
        self.fue_llamado = False
        self.imagen_recibida = None
        self.servicio_recibido = None
        self.imagen_guardada = None

    def insertar_imagen(self, objeto_usuario: AuthUser, imagen: TipadoImagenProtocol, servicio="usuarios") -> AuthUser:
        """
        Función para simular la inserción de una imagen.
        """
        objeto_usuario.imagen_url = f"{servicio}_imagen_ficticia.jpg"
        self.imagen_guardada = objeto_usuario.imagen_url
        self.fue_llamado = True
        self.imagen_recibida = imagen
        self.servicio_recibido = servicio
        return objeto_usuario