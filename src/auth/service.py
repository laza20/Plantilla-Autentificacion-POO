from sqlmodel import Session
from src.auth.models import AuthUser
from src.auth.utils import usuarios_utils
from typing import Dict
from jose import JWTError
from src.exceptions.domain import SinCargas, ContraseñaNoSegura
from src.exceptions.usuarios_exceptions import TokenInvalido, UsuarioNoEncontrado, UsuarioError, LoginError, TiempoInterrupcionInicioSesion
from src.exceptions.domain import DomainError
from src.auth import repository 
from src.cloudinary.cloudinary import insertar_imagen
from src.auth.security.security import hash_password, decode_token, verify_password
from src.auth.tokens.tokens import create_access_token, create_refresh_token
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def insertar_usuarios(session: Session, usuario: Dict) -> AuthUser:
    """
    Función para insertar un usuario en la base de datos.
    """
    if not usuario:
        raise SinCargas()
    
    objeto_usuario = usuarios_utils.normalizar_registro_a_cargar(usuario)
    verificacion_pass = usuarios_utils.validar_contraseña(objeto_usuario.password)

    if not verificacion_pass:
        raise ContraseñaNoSegura()
    
    objeto_usuario.password = hash_password(objeto_usuario.password)
    if objeto_usuario.imagen_url != None:
        objeto_usuario = insertar_imagen(objeto_usuario, servicio="usuarios")

    usuario_retornado = repository.insertar_y_retornar_registro(session, objeto_usuario)
    return usuario_retornado

def verificar_mail(token: str, session: Session):
    """
    Funcion encargada de verificar el mail del usuario utilizando un token de verificación.
    El token se decodifica para obtener el ID del usuario, luego se busca el usuario en la base de datos y se activa su cuenta.
    Si el token es inválido o el usuario no existe, se lanzan excepciones correspondientes
    """
    try:
        payload = decode_token(token)
        
        if payload.get("type") != "access":
            raise TokenInvalido()
                    
        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalido()

    except JWTError:
        raise TokenInvalido()

    try:
        user_id_db = int(user_id)
        usuario = repository.obtener_user_por_id_sin_activar(session, user_id_db)
        
        usuario = repository.activar_usuario(session, usuario)
        
    except UsuarioNoEncontrado:
        raise UsuarioNoEncontrado("El usuario asociado a este token no existe")
    
    tokens = {
        "access_token": create_access_token(str(usuario.id_usuario)),
        "refresh_token": create_refresh_token(str(usuario.id_usuario))
    }
    return tokens


def login_with_credentials(mail: str, password: str, session: Session):
    try:
        usuario_db = repository.buscar_y_retornar_user_por_mail_username(session, mail)
        usuario = usuario_db.model_dump()
            
        if not verify_password(password, usuario["password"]):
            raise LoginError("Usuario o contraseña incorrectos")

        return _emitir_tokens_usuario(usuario)
    
    except (UsuarioError, DomainError):
        raise
    except Exception as e:
        logger.exception("Error crítico en service")
        raise UsuarioError("Error al inicial sesion") from e
    
    
def _emitir_tokens_usuario(dict_usuario:Dict)->Dict:
        access_token = create_access_token(dict_usuario["id_usuario"])
        refresh_token = create_refresh_token(dict_usuario["id_usuario"])
        usuario_publico = usuarios_utils.retornar_usuario_publico(
            dict_usuario.get("email"), 
            dict_usuario.get("imagen_url")
            )


        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "usuario": usuario_publico
        }