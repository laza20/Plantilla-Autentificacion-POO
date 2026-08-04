from fastapi import FastAPI, UploadFile, File, HTTPException, status, Query
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from fastapi import UploadFile
from src.auth.domain.exceptions.domain import LimiteTamañoSuperado, ExtensionNoPermitida, ErrorCloudinary
from src.auth.infrastructure.images.cloudinary_config import cloudinary_uploader
from src.config.config import Settings, get_settings
from fastapi import Depends

app = FastAPI(title="FastAPI Cloudinary Integration")

"""
Servicios validos engloba todos los servicios que pueden utilizar imagenes dentro del sistema
Max_file_size es el tamaño máximo permitido para las imágenes a subir, en este caso 5MB.
"""
SERVICIOS_VALIDOS = ["usuarios", "example_1"]
MAX_FILE_SIZE = 5 * 1024 * 1024

"""
En caso de que mas servicios necesiten subir imagenes, se puede agregar el nombre del servicio a la lista 
SERVICIOS_VALIDOS y luego utilizar la función subir_imagen para subir la imagen al servicio 
correspondiente.
"""

class ImageService:
    def __init__(
        self,
        settings: Settings
    ):
        self.settings = settings

    def insertar_imagen(self, objeto:AuthUser, imagen: UploadFile, servicio:str)-> AuthUser:
        """
        Funcion encargada de eniar los datos a la funcion principal de subida de imagenes y actualizar el objeto con la URL optimizada y el public_id.
        - Recibe un objeto que contiene el campo imagen_url con el archivo a subir y el servicio al que pertenece la imagen.
        - Retorna el mismo objeto con los campos imagen_url e imagen_public_id actualizados con
        """
        subir_imagen_resultado = self.subir_imagen(servicio=servicio, imagen=imagen)
        objeto.imagen_url = subir_imagen_resultado["url_optimizada"]
        objeto.imagen_public_id = subir_imagen_resultado["public_id"]
        return objeto

    def subir_imagen(
        self,
        servicio: str,
        imagen: UploadFile,
        ):  
        """
        Funcion encargada de subir una imagen a Cloudinary, validando el servicio y la extensión del archivo.
        - Recibe el servicio al que pertenece la imagen y el archivo a subir.
        """
        if servicio.lower() not in SERVICIOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Servicio no válido. Opciones permitidas: {', '.join(SERVICIOS_VALIDOS)}"
            )

        extensiones_permitidas = ["jpg", "jpeg", "png", "webp"]
        file_ext = imagen.filename.split(".")[-1].lower() if "." in imagen.filename else ""

        if imagen.size > MAX_FILE_SIZE:
            raise LimiteTamañoSuperado()

        if file_ext not in extensiones_permitidas:
            raise ExtensionNoPermitida()

        try:
            carpeta_destino = f"{self.settings.NOMBRE_APP}/{servicio.lower()}"

            resultado = cloudinary_uploader.upload(
                imagen.file,
                folder=carpeta_destino,
                upload_preset=self.settings.CLOUDINARY_UPLOAD_PRESET,
                resource_type="image"
            )

            return {
                "mensaje": f"Imagen subida con éxito al módulo de {servicio.lower()}",
                "public_id": resultado.get("public_id"),
                "url_optimizada": resultado.get("secure_url"),
                "formato": resultado.get("format"),
                "tamaño_bytes": resultado.get("bytes")
            }
            
        except Exception as e:
            raise ErrorCloudinary(error=str(e))



def get_image_service(
    settings: Settings = Depends(get_settings)
):
    return ImageService(
        settings
    )