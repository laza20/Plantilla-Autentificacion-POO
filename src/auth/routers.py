from src.auth.models import LoginResponse, UserRegisterDTO, UsuarioCreado
from fastapi import APIRouter, Depends, status, Response, Path, Request, HTTPException, UploadFile
from src.auth.service import AuthService
from src.auth.use_cases.register import RegisterUseCase
from src.auth.use_cases.login import LoginUseCase
from src.auth.use_cases.verify_email import VerifyMailUseCase
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.use_cases.logout import LogoutUseCase
from src.container.dependencies import (
    get_register_use_case, get_login_use_case, get_verify_mail_use_case, get_user_validation_service, get_logout_service)
from src.exceptions.usuarios_exceptions import SinRefreshToken
from src.auth.transformers import parse_usuario_form
from src.config.config import settings
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.dependencies.dependencias import get_current_user
from src.exceptions.tokens import VerificacionInvalida, VerificacionExpirada

router = APIRouter(prefix=f"/{settings.NOMBRE_APP}/usuarios",
                   tags=["USUARIOS"],
                   responses={404:{"Message":"No encontrado"}}
)


@router.post("/registrar", response_model=UsuarioCreado, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos: tuple[UserRegisterDTO, UploadFile | None] = Depends(parse_usuario_form),
    register_use_case: RegisterUseCase = Depends(get_register_use_case)):
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
    usuario, imagen = datos
    usuario_nuevo = await register_use_case.register(usuario, imagen)
    return usuario_nuevo

@router.get("/verificar/{token}", status_code=status.HTTP_200_OK)
async def verificar_mail(
    response: Response,
    token: str = Path(..., description="Token de verificación enviado al correo"),
    verify_mail: VerifyMailUseCase = Depends(get_verify_mail_use_case)):
    """
    End point el cual permite la verificacion de una cuenta por medio de un token enviado al correo del usuario.
    """
    try:
        verify_mail.verificar_mail(token, response)
        return {"status": "success", "message": "¡Cuenta activada con éxito!"}
    except VerificacionExpirada:
        raise HTTPException(status_code=400, detail="Token expirado")
    except VerificacionInvalida:
        raise HTTPException(status_code=400, detail="Token inválido")


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_202_ACCEPTED)
async def logearse(
    response: Response,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
    usuario: OAuth2PasswordRequestForm = Depends()):

    logeado = login_use_case.login(usuario.username, usuario.password, response)
    return logeado

"""
@router.post("/Refresh/Token")
async def refresh_token(
    request: Request, 
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise SinRefreshToken("No hay refresh token en la cookie")

    auth_service.refreshed_token(refresh_token, response)

    return {"message": "Access token renovado"}
"""
@router.get("/user/current")
async def ver_usuario(
    current_user: dict = Depends(get_current_user),
    user_validation_service: UserValidationService = Depends(get_user_validation_service)):
    """
    End point encargado de devolver un usuario completo.
    """
    usuario = user_validation_service.get_user(current_user)
    return usuario

@router.post("/Logout")
async def logout(
    response: Response,
    logout_service: LogoutUseCase = Depends(get_logout_service)
    ):
    """
    End point encargado de desloguear un usuario.
    """
    logout_service.logout(response)
    return {"message": "Sesión cerrada"}