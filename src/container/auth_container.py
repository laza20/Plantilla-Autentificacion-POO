from src.config.config import Settings
from src.auth.utils.usuarios_utils import UserMapper
from src.auth.cookies.cookies import  CookiesService
from src.auth.service import AuthService
from src.domain.protocols.user_repository import UserRepositoryProtocol
from src.domain.protocols.token_service import TokenProtocol
from src.domain.protocols.password_service import PasswordProtocol
from src.domain.protocols.mail_service import MailProtocol
from src.domain.protocols.image_service import ImageProtocol


class AuthContainer:

    def __init__(
        self,
        settings: Settings,
        repository: UserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol, 
        mail_service: MailProtocol,        
        image_service: ImageProtocol       
    ):
        self.settings = settings
        self.repository = repository
        self.token_service = token_service
        self.password_service = password_service
        self.mail_service = mail_service
        self.image_service = image_service
        self.auth_service = AuthService(
            token_service=token_service,
            password_service=password_service,
            mail_service=mail_service,
            image_service=image_service,
            user_mapper=UserMapper(),
            cookies=CookiesService(settings),
            user_repository=repository,
            settings=settings
        )
