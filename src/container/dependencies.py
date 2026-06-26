from fastapi import Depends
from src.auth.repository import (UserRepository, get_user_repository)
from src.config.config import (Settings, get_settings)
from src.container.auth_container import AuthContainer
from src.auth.service import AuthService

from src.domain.protocols.token_service import TokenProtocol
from src.domain.protocols.password_service import PasswordProtocol
from src.domain.protocols.mail_service import MailProtocol
from src.domain.protocols.image_service import ImageProtocol
from src.auth.tokens.tokens import TokenService
from src.auth.security.security import PasswordService
from src.infrastructure.mail.mail import MailService
from src.infrastructure.images.cloudinary import ImageService



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


def get_auth_service(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository),
    token_service: TokenProtocol = Depends(get_token_service),
    password_service: PasswordProtocol = Depends(get_password_service),
    mail_service: MailProtocol = Depends(get_mail_service),
    image_service: ImageProtocol = Depends(get_image_service)
) -> AuthService:

    return AuthContainer(
        settings=settings,
        repository=repository,
        token_service=token_service,
        password_service=password_service,
        mail_service=mail_service,
        image_service=image_service
    ).auth_service