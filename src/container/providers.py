from fastapi import Depends
from sqlmodel import Session
from src.auth.infrastructure.persistence.postgres.auth_user_repository import AuthUserRepository
from src.auth.infrastructure.persistence.postgres.sesion_repository import SesionRepository
from src.config.config import Settings, get_settings
from src.container.auth_container import (
    ContainerRegister, ContainerLogin, 
    ContainerVerifyMail, ContainerLogout,
    ContainerRefreshToken, ContainerListarSesiones, ContainerEliminarSesiones)
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.application.use_cases.eliminar_sesiones import EliminarSesionesUseCase
from src.auth.application.use_cases.listar_sesiones import ListarSesionesUseCase
from src.auth.domain.protocols.sesion_repository import TokenRepositoryProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.user_repository import UsuarioRepositoryProtocol
from src.auth.infrastructure.persistence.postgres.usuario_repository import UserRepository
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.infrastructure.security.tokens.tokens import TokenService
from src.auth.infrastructure.security.security import PasswordService
from src.auth.infrastructure.mail.mail import MailService
from src.auth.infrastructure.images.cloudinary import ImageService
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.application.use_cases.register import RegisterUseCase
from src.auth.application.use_cases.login import LoginUseCase
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.database.client import get_session
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.application.use_cases.logout import LogoutUseCase
from src.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.auth.domain.services.mail_policy import MailPolicyService

def get_user_repository(session: Session = Depends(get_session)) -> UsuarioRepositoryProtocol:
    return UserRepository(session)

def get_auth_user_repository(session: Session = Depends(get_session)) -> AuthUserRepository:
    return AuthUserRepository(session)

def get_user_validation_service(
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
    settings: Settings = Depends(get_settings)
) -> UserValidationService:
    return UserValidationService(
        auth_user_repository=auth_user_repository, 
        settings=settings
    )

def get_cookies_service(settings: Settings = Depends(get_settings)) -> CookiesService:
    return CookiesService(settings=settings)

def get_token_repository(session: Session = Depends(get_session)) -> TokenRepositoryProtocol:
    return SesionRepository(session)

def get_token_service(
    settings: Settings = Depends(get_settings)
) -> TokenProtocol:
    return TokenService(settings)


def get_password_service(
    settings: Settings = Depends(get_settings)
) -> PasswordProtocol:
    return PasswordService(settings)


def get_mail_service(
    settings: Settings = Depends(get_settings)
) -> MailProtocol:
    return MailService(settings)


def get_image_service(
    settings: Settings = Depends(get_settings)
) -> ImageProtocol:
    return ImageService(settings)

def get_password_policy(settings: Settings = Depends(get_settings)) -> PasswordPolicyService:
    return PasswordPolicyService()

def get_mail_policy(settings: Settings = Depends(get_settings)) -> MailPolicyService:
    return MailPolicyService()

def get_register_use_case(
    settings: Settings = Depends(get_settings),
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    password_policy: PasswordPolicyService = Depends(get_password_policy),
    mail_service: MailProtocol = Depends(get_mail_service),
    image_service: ImageProtocol = Depends(get_image_service),
    mail_policy : MailPolicyService = Depends(get_mail_policy),
    usuario_repository: UsuarioRepositoryProtocol = Depends(get_user_repository)
) -> RegisterUseCase:

    return ContainerRegister(
        settings=settings,
        auth_user_repository=auth_user_repository,
        token_service=token_service,
        password_service=password_service,
        password_policy=password_policy,
        mail_service=mail_service,
        image_service=image_service,
        mail_policy=mail_policy,
        usuario_repository=usuario_repository
    ).register_use_case


def get_login_use_case(
    settings: Settings = Depends(get_settings),
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    cookies_service: CookiesService = Depends(get_cookies_service),
    user_validation_service: UserValidationService = Depends(get_user_validation_service),
    token_repository: TokenRepositoryProtocol = Depends(get_token_repository)
) -> LoginUseCase:

    return ContainerLogin(
        settings=settings,
        auth_user_repository=auth_user_repository,
        token_service=token_service,
        password_service=password_service,
        cookies_service=cookies_service,
        user_validation_service=user_validation_service,
        token_repository=token_repository
    ).login_use_case


def get_verify_mail_use_case(
    settings: Settings = Depends(get_settings),
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
    cookies_service: CookiesService = Depends(get_cookies_service),
    token_service: TokenProtocol = Depends(get_token_service)
) -> VerifyMailUseCase:

    return ContainerVerifyMail(
        settings=settings,
        auth_user_repository=auth_user_repository,
        cookies_service=cookies_service,
        token_service=token_service
    ).verify_mail_use_case

def get_logout_service(
    cookies_service: CookiesService = Depends(get_cookies_service),
    token_service: TokenProtocol = Depends(get_token_service),
    token_repository: TokenRepositoryProtocol = Depends(get_token_repository)
)-> LogoutUseCase:
    return ContainerLogout(
        cookies_service=cookies_service,
        token_service=token_service,
        token_repository=token_repository
        ).logout_use_case


def get_refresh_token_service(
    cookies_service: CookiesService = Depends(get_cookies_service),
    token_service: TokenProtocol = Depends(get_token_service)
)-> RefreshTokenUseCase:
    return ContainerRefreshToken(
        cookies_service=cookies_service,
        token_service=token_service
        ).refresh_token_use_case


def get_listar_sesiones_use_case(
    token_repository: TokenRepositoryProtocol = Depends(get_token_repository)
) -> ListarSesionesUseCase:
    return ContainerListarSesiones(token_repository=token_repository).listar_sesiones_use_case

def get_eliminar_sesiones_use_case(
    token_repository: TokenRepositoryProtocol = Depends(get_token_repository)
) -> EliminarSesionesUseCase:
    return ContainerEliminarSesiones(token_repository=token_repository).eliminar_sesiones_use_case

