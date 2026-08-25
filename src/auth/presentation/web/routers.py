from src.auth.infrastructure.persistence.postgres.models_auth_users import LoginResponse, UserRegisterDTO, UsuarioCreado
from fastapi import APIRouter, Depends, status, Response, Path, HTTPException, UploadFile, Request
from src.auth.presentation.web.utils.request_metadata import RequestMetadata
from src.auth.application.use_cases.register import RegisterUseCase
from src.auth.application.use_cases.listar_sesiones import ListarSesionesUseCase
from src.auth.application.use_cases.login import LoginUseCase
from src.auth.application.use_cases.eliminar_sesiones import EliminarSesionesUseCase
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.application.use_cases.logout import LogoutUseCase
from src.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.auth.application.use_cases.recover_password.solicitud_recuperacion import SolicitudRecuperacionUseCase
from src.auth.application.use_cases.recover_password.verificar_token import VerificarTokenUseCase
from src.container.providers import (
    get_register_use_case, get_login_use_case, 
    get_verify_mail_use_case, get_user_validation_service, 
    get_logout_service, get_refresh_token_service, get_listar_sesiones_use_case,
    get_eliminar_sesiones_use_case, get_solicitud_recuperacion_contraseña_use_case,
    get_verificar_token_recuperacion_contraseña_use_case, get_cookies_service)
from src.auth.domain.exceptions.usuarios_exceptions import SinRefreshToken
from src.auth.application.dtos import parse_usuario_form
from src.config.config import settings
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.presentation.web.guards import get_current_user
from src.auth.domain.exceptions.tokens import VerificacionInvalida, VerificacionExpirada
from src.auth.infrastructure.persistence.postgres.schemas.schemas_recepcion import SolicitudRecuperacionRequest

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
    usuario_nuevo = await register_use_case.ejecutar(usuario, imagen)
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
        verify_mail.ejecutar(token, response)
        return {"status": "success", "message": "¡Cuenta activada con éxito!"}
    except VerificacionExpirada:
        raise HTTPException(status_code=400, detail="Token expirado")
    except VerificacionInvalida:
        raise HTTPException(status_code=400, detail="Token inválido")


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_202_ACCEPTED)
async def logearse(
    response: Response,
    request: Request,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
    usuario: OAuth2PasswordRequestForm = Depends()):

    request_metadata = RequestMetadata(request)
    ip = request_metadata.get_ip()
    user_agent = request_metadata.get_user_agent()

    logeado = login_use_case.ejecutar(usuario.username, usuario.password, ip, user_agent, response)
    return logeado


@router.post("/Refresh/Token")
async def refresh_token(
    request: Request, 
    response: Response,
    refresh_token_service: RefreshTokenUseCase = Depends(get_refresh_token_service)):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise SinRefreshToken("No hay refresh token en la cookie")

    refresh_token_service.ejecutar(refresh_token, response)

    return {"message": "Access token renovado"}


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
    request: Request,
    logout_service: LogoutUseCase = Depends(get_logout_service)
    ):
    """
    End point encargado de desloguear un usuario.
    """
    refresh_token = request.cookies.get("refresh_token")
    logout_service.ejecutar(refresh_token=refresh_token,response=response)
    return {"message": "Sesión cerrada"}


@router.get("/listar_sesiones")
async def list_sesions(
    request: Request,
    user_validation_service: UserValidationService = Depends(get_user_validation_service),
    listar_sesiones_use_case: ListarSesionesUseCase = Depends(get_listar_sesiones_use_case),
    current_user: dict = Depends(get_current_user)
):
    """
    End point encargado de listar las sesiones activas de un usuario.
    """
    ip = RequestMetadata(request).get_ip()
    id_usuario = user_validation_service.get_user(current_user).id_usuario
    return listar_sesiones_use_case.ejecutar(id_usuario=id_usuario, ip=ip)


@router.delete("/eliminar_sesion/{id_sesion}")
async def eliminar_sesion(
    id_sesion: int = Path(..., description="ID de la sesión a eliminar"),
    user_validation_service: UserValidationService = Depends(get_user_validation_service),
    eliminar_sesiones_use_case: EliminarSesionesUseCase = Depends(get_eliminar_sesiones_use_case),
    current_user: dict = Depends(get_current_user)
):
    """
    End point encargado de eliminar una sesión activa de un usuario.
    """
    id_usuario = user_validation_service.get_user(current_user).id_usuario
    resultado = eliminar_sesiones_use_case.ejecutar(id_sesion=id_sesion, id_usuario=id_usuario)
    return resultado


@router.post("/solicitud/recuperacion")
async def solicitud_recuperacion(
    body: SolicitudRecuperacionRequest,
    solicitur_recuperacion_use_case: SolicitudRecuperacionUseCase = Depends(get_solicitud_recuperacion_contraseña_use_case)
):
    resultado = await solicitur_recuperacion_use_case.ejecutar(body.email)
    return resultado


@router.get("/recuperar/password/{token}", status_code=status.HTTP_200_OK)
async def verificar_token_recuperacion(
    response: Response,
    token: str = Path(..., description="Token de recuperacion enviado al correo"),
    verificar_token_recuperacion_contraseña_use_case: VerificarTokenUseCase = Depends(get_verificar_token_recuperacion_contraseña_use_case),
    cookies_service: CookiesService = Depends(get_cookies_service)):
    """
    End point el cual permite la recuperacion de una contraseña por medio de un token enviado al correo del usuario.
    """
    reset_token = verificar_token_recuperacion_contraseña_use_case.ejecutar(token)
    cookies_service.set_reset_cookie(
        reset_token=reset_token,
        response=response,
        url=f"/{settings.NOMBRE_APP}/usuarios/recuperar/contraseña"
    )
    
    return {"message": "Configuracion realizada correctamente."}