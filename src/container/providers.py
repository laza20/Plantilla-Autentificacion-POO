from fastapi import Depends
from sqlmodel import Session
from src.auth.infrastructure.persistence.postgres.user_repository import UserRepository
from src.config.config import Settings, get_settings
from src.container.auth_container import (
    ContainerRegister, ContainerLogin, 
    ContainerVerifyMail, ContainerLogout,
    ContainerRefreshToken)
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.domain.protocols.token_service import TokenProtocol
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

def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

def get_user_validation_service(
    repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings)
) -> UserValidationService:
    return UserValidationService(
        user_repository=repository, 
        settings=settings
    )

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
    cookies_service: CookiesService = Depends(get_cookies_service),
    user_validation_service: UserValidationService = Depends(get_user_validation_service)
) -> LoginUseCase:

    return ContainerLogin(
        settings=settings,
        repository=repository,
        token_service=token_service,
        password_service=password_service,
        cookies_service=cookies_service,
        user_validation_service=user_validation_service
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

def get_logout_service(
    cookies_service: CookiesService = Depends(get_cookies_service)
)-> LogoutUseCase:
    return ContainerLogout(
        cookies_service=cookies_service
        ).logout_use_case


def get_refresh_token_service(
    cookies_service: CookiesService = Depends(get_cookies_service),
    token_service: TokenProtocol = Depends(get_token_service)
)-> RefreshTokenUseCase:
    return ContainerRefreshToken(
        cookies_service=cookies_service,
        token_service=token_service
        ).refresh_token_use_case