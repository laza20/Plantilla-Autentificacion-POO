from src.auth.models import AuthUser, LoginResponse
from fastapi import APIRouter, Depends, status, Response, Path, Request
from typing import Dict
from sqlmodel import Session
from src.database.client import get_session
from src.auth.tokens.tokens import refreshed_token
from src.exceptions.usuarios_exceptions import SinRefreshToken
from src.auth import service
from src.auth.transformers import parse_usuario_form
from src.config.config import settings
from src.utils import mail
from src.auth.tokens.tokens import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.dependencies.dependencias import get_current_user

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
    request: Request,
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
            url=f"{settings.BASE_URL}/{settings.NOMBRE_APP}/usuarios/verificar/{token_verificacion}",
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

@router.get("/verificar/{token}", status_code=status.HTTP_200_OK)
async def verificar_mail(
    token: str = Path(..., description="Token de verificación enviado al correo"),
    session: Session = Depends(get_session),
    response: Response = Response()):
    """
    End point el cual permite la verificacion de una cuenta por medio de un token enviado al correo del usuario.
    """
    try:
        tokens = service.verificar_mail(token, session)
        
        cookies = _cookies_setings()
        response.set_cookie(key="access_token", value=tokens["access_token"], max_age=15 * 60, **cookies)
        response.set_cookie(key="refresh_token", value=tokens["refresh_token"], max_age=7 * 24 * 60 * 60, **cookies)
        
        return {"status": "success", "message": "¡Cuenta activada con éxito! Ya puedes usar la plataforma."}
    except Exception as e:
        raise Exception({"status": "error",   
                        "message": "Error al verificar el correo electrónico."}) from e


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_202_ACCEPTED)
async def logearse(
    request: Request, 
    response: Response, 
    session: Session = Depends(get_session),
    usuario: OAuth2PasswordRequestForm = Depends()):
    logeado = service.login_with_credentials(usuario.username, usuario.password, session)
    
    cookies = _cookies_setings()
    response.set_cookie(
            key="access_token",
            value=logeado["access_token"],
            max_age=15 * 60,
            **cookies 
        )

    response.set_cookie(
        key="refresh_token",
        value=logeado["refresh_token"],
        max_age=7 * 24 * 60 * 60,
        **cookies
    )

    return logeado


@router.post("/Refresh/Token")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise SinRefreshToken("No hay refresh token en la cookie")

    nuevo_token = refreshed_token(refresh_token)
    cookies = _cookies_setings()

    response.set_cookie(
        key="access_token",
        value=nuevo_token["access_token"],
        max_age=15 * 60,
        **cookies
    )

    return {"message": "Access token renovado"}

@router.get("/user/current")
async def ver_usuario(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)):
    """
    End point encargado de devolver un usuario completo.
    """
    usuario = service.get_user(current_user, session)
    return usuario

@router.post("/Logout")
async def logout(response: Response):
    """
    End point encargado de desloguear un usuario.
    """
    cookie_params = {
        "path": "/",
        "httponly": True,
        "samesite": "lax",
        "secure": False  
    }
    response.delete_cookie("access_token", **cookie_params)
    response.delete_cookie("refresh_token", **cookie_params)
    return {"message": "Sesión cerrada"}