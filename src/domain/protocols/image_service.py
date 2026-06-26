from typing import Protocol, runtime_checkable
from src.auth.models import AuthUser
from fastapi import UploadFile

@runtime_checkable
class ImageProtocol(Protocol):
    """
    Contrato para servicios de gestión de imágenes en la plantilla.
    
    ¿Qué es?
    --------
    Define la interfaz que CUALQUIER servicio de imágenes debe cumplir.
    Puede ser Cloudinary, AWS S3, Azure Blob, Google Cloud Storage, etc.
    
    ¿Cómo implementar?
    ------------------
    1. Crea una clase que implemente estos métodos
    2. Asegúrate de que cumple exactamente esta firma
    3. Registra la clase en dependencies.py
    
    Ejemplo de implementación (Cloudinary):
    
    class CloudinaryImageService:
        def __init__(self, settings: Settings):
            self.settings = settings
        
        def insertar_imagen(self, objeto: AuthUser, servicio: str) -> AuthUser:
            # 1. Valida el archivo en objeto.imagen_url
            # 2. Sube a Cloudinary (método privado)
            # 3. Actualiza objeto.imagen_url con URL pública
            # 4. Actualiza objeto.imagen_public_id con ID del servidor
            return objeto
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa los métodos.
    
    Métodos requeridos:
    -------------------
    """
    
    def insertar_imagen(self, objeto:AuthUser, imagen:UploadFile, servicio: str) -> AuthUser:
        """
        Inserta/procesa una imagen asociada a un usuario.
        
        Parámetros:
        -----------
        objeto : AuthUser
            Objeto del usuario que será actualizado.
            
            IMPORTANTE sobre objeto.imagen_url:
            - Es el dato clave que contiene la imagen
            - Puede venir en distintos formatos según tu aplicación:
              * UploadFile (si viene de un POST /upload)
              * Base64 encoded string
              * URL de otra fuente
            Tu implementación debe manejar el formato que uses.
        
        servicio : str
            Contexto/categoría donde se usa la imagen.
            Ejemplos: "usuarios", "productos", "posts"
            Usado para organizar carpetas en el servidor.
        
        Retorna:
        --------
        AuthUser
            El MISMO objeto de entrada, con estos campos actualizados:
            
            - imagen_url: URL PÚBLICA donde el cliente puede acceder la imagen
              Ejemplo: "https://res.cloudinary.com/mycloud/image/upload/..."
            
            - imagen_public_id: ID único generado por el servidor
              Ejemplo: "myapp/usuarios/user123"
              Sirve para actualizar/eliminar después
        
        Excepciones esperadas:
        ----------------------
        LimiteTamañoSuperado
            Si el archivo supera el límite (ej: 5MB)
        
        ExtensionNoPermitida
            Si la extensión no es jpg/jpeg/png/webp
        
        ErrorCloudinary (o equivalente)
            Si falla la comunicación con el servidor de imágenes
        
        Ejemplo práctico:
        -----------------
        >>> usuario = AuthUser(id_usuario=1, email="juan@example.com")
        >>> usuario.imagen_url = <UploadFile desde formulario>
        >>> 
        >>> imagen_service = CloudinaryImageService(settings)
        >>> usuario_actualizado = imagen_service.insertar_imagen(usuario, "usuarios")
        >>> 
        >>> # Ahora:
        >>> print(usuario_actualizado.imagen_url)
        # https://res.cloudinary.com/myapp/image/upload/myapp/usuarios/abc123.jpg
        >>> print(usuario_actualizado.imagen_public_id)
        # myapp/usuarios/abc123
        
        Notas de implementación:
        -----------------------
        - La imagen en objeto.imagen_url es el "input" que debes procesar
        - Valida: tamaño, extensión, formato
        - Sube al servidor (Cloudinary, S3, etc.)
        - Extrae la URL pública y el ID único
        - Actualiza el objeto y retórnalo
        - Si algo falla, lanza una excepción
        - El cliente NO debería preocuparse por detalles internos
        """
        ...