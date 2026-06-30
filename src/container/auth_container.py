from src.config.config import Settings
from src.auth.cookies.cookies import CookiesService
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.use_cases.register import RegisterUseCase
from src.auth.use_cases.login import LoginUseCase
from src.auth.use_cases.verify_email import VerifyMailUseCase
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.use_cases.logout import LogoutUseCase
from src.auth.use_cases.refresh_token import RefreshTokenUseCase


class ContainerRegister:
    def __init__(
        self,
        settings: Settings,
        repository: UserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol, 
        mail_service: MailProtocol,        
        image_service: ImageProtocol,
        password_policy: PasswordPolicyService
    ):
        self.settings = settings
        self.repository = repository
        self.token_service = token_service
        self.password_service = password_service
        self.mail_service = mail_service
        self.image_service = image_service
        self.password_policy = password_policy
    @property
    def register_use_case(self) -> RegisterUseCase:

        return RegisterUseCase(
            settings=self.settings,
            user_repository=self.repository,
            password_service=self.password_service,
            password_policy=self.password_policy,
            mail_service=self.mail_service,
            image_service=self.image_service,
            token_service=self.token_service,
            
        )
class ContainerLogin:
    def __init__(
        self,
        settings: Settings,
        repository: UserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol,
        cookies_service: CookiesService,
        user_validation_service: UserValidationService
    ):
        self.settings = settings
        self.repository = repository
        self.token_service = token_service
        self.password_service = password_service
        self.cookies_service = cookies_service
        self.user_validation_service = user_validation_service
        

    @property
    def login_use_case(self) -> LoginUseCase:

        return LoginUseCase(
            settings=self.settings,
            user_repository=self.repository,
            token_service=self.token_service,
            password_service=self.password_service,
            cookies_service = self.cookies_service,
            user_validation_service = self.user_validation_service
        )

class ContainerVerifyMail:
    def __init__(
        self,
        settings: Settings,
        repository: UserRepositoryProtocol,
        token_service: TokenProtocol,
        cookies_service: CookiesService
    ):
        self.settings = settings
        self.repository = repository
        self.token_service = token_service
        self.cookies_service = cookies_service
    @property
    def verify_mail_use_case(self) -> VerifyMailUseCase:

        return VerifyMailUseCase(
            repository=self.repository,
            settings=self.settings,
            cookies_service=self.cookies_service,
            token_service=self.token_service
        )
    

class ContainerLogout:
    def __init__(
        self,
        cookies_service: CookiesService
    ):
        self.cookies_service = cookies_service
    @property
    def logout_use_case(self) -> LogoutUseCase:

        return LogoutUseCase(
            cookies_service=self.cookies_service
        )
    
class ContainerRefreshToken:
    def __init__(
        self,
        cookies_service: CookiesService,
        token_service: TokenProtocol
    ):
        self.cookies_service = cookies_service
        self.token_service = token_service
    @property
    def refresh_token_use_case(self) -> RefreshTokenUseCase:

        return RefreshTokenUseCase(
            cookies_service=self.cookies_service,
            token_service = self.token_service
        )