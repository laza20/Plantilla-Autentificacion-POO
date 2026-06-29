from fastapi import Depends
from src.auth.repository import (UserRepository, get_user_repository)
from src.config.config import (Settings, get_settings)
from src.container.auth_container import ContainerRegister, ContainerLogin, ContainerVerifyMail, AuthContainer
from src.auth.cookies.cookies import CookiesService
from src.auth.service import AuthService
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.tokens.tokens import TokenService
from src.auth.security.security import PasswordService
from src.infrastructure.mail.mail import MailService
from src.infrastructure.images.cloudinary import ImageService
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.use_cases.register import RegisterUseCase
from src.auth.use_cases.login import LoginUseCase
from src.auth.use_cases.verify_email import VerifyMailUseCase


def get_cookies_service(settings: Settings = Depends(get_settings)) -> CookiesService:
    return CookiesService(settings=settings)

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


def get_auth_service(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    password_policy: PasswordPolicyService = Depends(get_password_policy),
    mail_service: MailProtocol = Depends(get_mail_service),
    image_service: ImageProtocol = Depends(get_image_service)
) -> AuthContainer:

    return ContainerRegister(
        settings=settings,
        repository=repository,
        token_service=token_service,
        password_service=password_service,
        password_policy=password_policy,
        mail_service=mail_service,
        image_service=image_service
    ).register_use_case

def get_register_use_case(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    password_policy: PasswordPolicyService = Depends(get_password_policy),
    mail_service: MailProtocol = Depends(get_mail_service),
    image_service: ImageProtocol = Depends(get_image_service)
) -> RegisterUseCase:

    return ContainerRegister(
        settings=settings,
        repository=repository,
        token_service=token_service,
        password_service=password_service,
        password_policy=password_policy,
        mail_service=mail_service,
        image_service=image_service
    ).register_use_case


def get_login_use_case(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    cookies_service: CookiesService = Depends(get_cookies_service)
) -> LoginUseCase:

    return ContainerLogin(
        settings=settings,
        repository=repository,
        token_service=token_service,
        password_service=password_service,
        cookies_service=cookies_service
    ).login_use_case


def get_verify_mail_use_case(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository),
    cookies_service: CookiesService = Depends(get_cookies_service),
    token_service: TokenProtocol = Depends(get_token_service)
) -> VerifyMailUseCase:

    return ContainerVerifyMail(
        settings=settings,
        repository=repository,
        cookies_service=cookies_service,
        token_service=token_service
    ).verify_mail_use_case