from typing import List, Dict
from src.auth.models import AuthUser, AuthUserNoImage
from pydantic import ValidationError
from exceptions.domain import LongitudExcedida
import re

def normalizar_registro_a_cargar(usuario: Dict) -> AuthUser:
    """
    Funcion encargada de normalizar los datos del usuario antes de ser insertados en la base de datos.
    - Datos limpios debe utilizarse para los datos str con una longitud maxima definida.
    - Valida que la imagen no exceda el tamaño máximo permitido.
    """
    try:
        file_binario = usuario.get("imagen_url")
        datos_limpios = usuario | {
            "mail": usuario.get("email", "").strip().lower(),            
        }
        
        datos_para_validar = datos_limpios | {"imagen_url": None} if file_binario else datos_limpios
        
        usuario_validado = AuthUserNoImage(**datos_para_validar)
        usuario_orm = AuthUser(**usuario_validado.model_dump())
        
        if file_binario is not None and getattr(file_binario, "filename", "") != "":
            usuario_orm.imagen_url = file_binario
        else:
            usuario_orm.imagen_url = usuario.get("imagen_url") if isinstance(usuario.get("imagen_url"), str) else None
        
        return usuario_orm

    except ValidationError as e:
        error_detalle = e.errors()[0]
        campo_afectado = error_detalle.get("loc", ["campo"])[0]
        
        if error_detalle.get("type") == "string_too_long":
            raise LongitudExcedida(
                message=f"El campo '{campo_afectado}' excede el tamaño máximo permitido."
            )
        raise e


def validar_contraseña(contraseña: str) -> bool:
    """
    Valida que la contraseña cumpla con los requisitos de seguridad.
    Requisitos:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    
    if len(contraseña) < 8:
        return False
    if not re.search(r'[A-Z]', contraseña):
        return False
    if not re.search(r'[a-z]', contraseña):
        return False
    if not re.search(r'[0-9]', contraseña):
        return False
    if not re.search(r'[^a-zA-Z0-9]', contraseña):
        return False
    
    return True