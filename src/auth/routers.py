from src.auth.models import AuthUser
from fastapi import APIRouter, Depends, status, Response, Query
from typing import Dict
from sqlmodel import Session
from src.database.client import get_session
from src.auth import service
from src.auth.transformers import parse_usuario_form
from src.config.config import settings
from src.auth.utils import mail
from src.auth.tokens.tokens import create_access_token

router = APIRouter(prefix=f"/{settings.NOMBRE_APP}/usuarios",
                   tags=["USUARIOS"],
                   responses={404:{"Message":"No encontrado"}}
)

def _cookies_setings():
    is_prod = settings.is_prod
    cookie_settings = {
            "httponly": True,
            "secure": is_prod,    
            "samesite": "none" if is_prod else "lax",
            "path": "/",
        }
    return cookie_settings

@router.post("/registrar", response_model=AuthUser, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    usuario: Dict = Depends(parse_usuario_form),
    session: Session = Depends(get_session),
    response: Response = Response()):
    """
    La funcion registrar hace lo siguiente:
    1. Recibe un diccionario con los datos del usuario a registrar.
    2. Valida que el diccionario no esté vacío.
    3. Normaliza los datos del usuario para asegurarse de que estén en el formato correcto.
    4. Valida que la contraseña cumpla con los requisitos de seguridad.
    5. Hashea la contraseña para almacenarla de forma segura en la base de datos.
    6. Confirma que el mail ingresado exista y sea válido.
    7. Inserta el nuevo usuario en la base de datos.
    8. Devuelve el nuevo usuario creado.
    """
    nuevos_usuarios = service.insertar_usuarios(session, usuario)
    token_verificacion = create_access_token(str(nuevos_usuarios.id_usuario))
    try:
        cuerpo_correo = mail.generar_correo_verificacion(
            url=f"/{settings.BASE_URL}/{settings.NOMBRE_APP}/verificar/{token_verificacion}",
            nombre_proyecto=settings.NOMBRE_APP
        )
        await mail.enviar_mail(
            email_destino=nuevos_usuarios.email,
            cuerpo_html=cuerpo_correo
        )   
    except Exception as e:
        print(e)
        raise Exception(e) from e
    return nuevos_usuarios