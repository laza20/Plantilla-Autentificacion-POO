from typing import Protocol, runtime_checkable
from fastapi import UploadFile
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser

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
    1. Crea una clase que implemente este método
    2. Asegúrate de cumplir exactamente esta firma
    3. Registra la clase en dependencies.py
    
    Ejemplo de implementación (Cloudinary):
    
    class CloudinaryImageService:
        def __init__(self, settings: Settings):
            self.settings = settings
        
        def insertar_imagen(self, objeto: AuthUser, imagen: UploadFile, servicio: str) -> AuthUser:
            # 1. Valida el archivo (tamaño, extensión)
            # 2. Sube a Cloudinary (método privado _subir_imagen)
            # 3. Actualiza objeto.imagen_url con URL pública
            # 4. Actualiza objeto.imagen_public_id con ID del servidor
            # 5. Retorna el objeto actualizado
            resultado = self._subir_imagen(servicio, imagen)
            objeto.imagen_url = resultado["url_optimizada"]
            objeto.imagen_public_id = resultado["public_id"]
            return objeto
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa el método.
    
    Métodos requeridos:
    -------------------
    """
    
    def insertar_imagen(self, objeto: AuthUser, imagen: UploadFile, servicio: str) -> AuthUser:
        """
        Procesa y almacena una imagen, actualizando el objeto del usuario con la información del servidor.
        
        Responsabilidad completa:
        -------------------------
        Este método encapsula TODO lo relacionado con imágenes:
        1. Validación (tamaño, extensión, formato)
        2. Upload al proveedor (Cloudinary, S3, etc.)
        3. Actualización del objeto usuario
        4. Retorno del objeto modificado
        
        El cliente (AuthService) NO ve detalles internos.
        
        Parámetros:
        -----------
        objeto : AuthUser
            Objeto del usuario que será actualizado.
            Los campos imagen_url e imagen_public_id serán modificados.
            
            Campos modificados:
            - objeto.imagen_url: Se actualiza con la URL pública
            - objeto.imagen_public_id: Se actualiza con el ID del servidor
        
        imagen : UploadFile
            Archivo subido por el usuario (viene de un formulario/request).
            Contiene:
            - imagen.filename: Nombre del archivo (ej: "foto.jpg")
            - imagen.file: Objeto file que puedes leer
            - imagen.size: Tamaño en bytes
            - imagen.content_type: MIME type (ej: "image/jpeg")
            
            Nota: Tu implementación debe validar este archivo.
        
        servicio : str
            Contexto/categoría donde se usa la imagen.
            Ejemplos: "usuarios", "productos", "posts"
            
            Usado para:
            - Organizar carpetas en el servidor
            - Validar que el servicio es permitido
            - Prefixar el ID de la imagen en el servidor
        
        Retorna:
        --------
        AuthUser
            El MISMO objeto pasado como parámetro, pero MODIFICADO:
            
            - objeto.imagen_url: 
              Ahora contiene la URL PÚBLICA donde acceder la imagen
              Ejemplo: "https://res.cloudinary.com/mycloud/image/upload/..."
              Esta URL es lo que guardas en BD y lo que sirves al cliente
            
            - objeto.imagen_public_id:
              Ahora contiene el ID único generado por el servidor
              Ejemplo: "myapp/usuarios/abc123"
              Sirve para actualizar/eliminar la imagen después
        
        Excepciones esperadas:
        ----------------------
        LimiteTamañoSuperado
            Si imagen.size > MAX_FILE_SIZE (típicamente 5MB)
            
            Ejemplo: Usuario sube una imagen de 10MB
            >>> raise LimiteTamañoSuperado()
        
        ExtensionNoPermitida
            Si la extensión del archivo no está en permitidas
            
            Ejemplo: Usuario sube "documento.pdf"
            Extensiones permitidas: jpg, jpeg, png, webp
            >>> raise ExtensionNoPermitida()
        
        ErrorCloudinary (o equivalente para tu proveedor)
            Si falla la comunicación con el servidor de imágenes
            
            Razones: Credenciales inválidas, quota excedida, timeout, etc.
            >>> raise ErrorCloudinary(error=str(e))
        
        Ejemplo práctico (flujo completo):
        ----------------------------------
        # En AuthService.register()
        usuario = AuthUser(id_usuario=1, email="juan@example.com")
        
        # imagen viene como parámetro del POST (FormData)
        imagen = request.files["profile_picture"]  # UploadFile
        
        # Llamas el servicio
        usuario_actualizado = self.image_service.insertar_imagen(
            objeto=usuario,
            imagen=imagen,
            servicio="usuarios"
        )
        
        # Resultado:
        print(usuario_actualizado.imagen_url)
        # https://res.cloudinary.com/myapp/image/upload/myapp/usuarios/abc123.jpg
        
        print(usuario_actualizado.imagen_public_id)
        # myapp/usuarios/abc123
        
        # Ahora guardas el usuario en BD con estos datos
        usuario_creado = self.auth_user_repository.insertar(usuario_actualizado)
        
        Notas de implementación:
        -----------------------
        - La imagen viene como UploadFile (parámetro explícito)
        - Valida: tamaño, extensión, formato
        - Sube al servidor (Cloudinary, S3, etc.)
        - Extrae la URL pública y el ID único
        - Actualiza el objeto proporcionado
        - Retorna el objeto modificado
        - Si algo falla, lanza la excepción correspondiente
        - El cliente NO debería preocuparse por detalles internos
        
        Ventajas de este diseño:
        -----------------------
        1. Responsabilidad única: ImageService maneja TODO de imágenes
        2. Encapsulación: AuthService no ve detalles (validación, upload)
        3. Testeable: Puedes mockear fácilmente con FakeImageService
        4. Flexible: Cambiar de Cloudinary a S3 solo requiere cambiar dependencies.py
        5. Limpio: AuthService es simple y legible
        
        Ejemplo de uso en router (si lo necesitas):
        -------------------------------------------
        @router.post("/usuarios/registro")
        async def register(
            usuario_data: UserRegisterDTO,
            imagen: UploadFile = File(None),  # Opcional
            auth_service: AuthService = Depends(get_auth_service)
        ):
            usuario = auth_service.register_with_image(
                usuario_data=usuario_data,
                imagen=imagen  # Pasa aquí
            )
            return usuario
        """
        ...