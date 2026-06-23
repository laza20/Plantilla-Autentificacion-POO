from src.auth.repository import UserRepository
from src.auth.tokens.tokens import TokenService
from src.auth.security.security import PasswordService
from src.config.config import Settings
from src.utils.mail import MailService
from src.cloudinary.cloudinary import ImageService
from src.auth.utils.usuarios_utils import UserMapper
from src.auth.cookies.cookies import  CookiesService
from src.auth.service import AuthService

class AuthContainer:

    def __init__(
        self,
        settings: Settings,
        repository: UserRepository
    ):

        self.auth_service = AuthService(
            token_service=TokenService(settings),
            password_service=PasswordService(settings),
            mail_service=MailService(settings),
            image_service=ImageService(settings),
            user_mapper=UserMapper(),
            cookies=CookiesService(settings),
            user_repository=repository,
            settings=settings
        )
