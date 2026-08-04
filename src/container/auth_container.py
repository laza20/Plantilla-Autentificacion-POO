from src.config.config import Settings
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.domain.protocols.auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.user_repository import UsuarioRepositoryProtocol
from src.auth.domain.protocols.token_repository import TokenRepositoryProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.application.use_cases.register import RegisterUseCase
from src.auth.application.use_cases.login import LoginUseCase
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.application.use_cases.logout import LogoutUseCase
from src.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.auth.domain.services.mail_policy import MailPolicyService


class ContainerRegister:
    def __init__(
        self,
        settings: Settings,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol, 
        mail_service: MailProtocol,        
        image_service: ImageProtocol,
        password_policy: PasswordPolicyService,
        mail_policy : MailPolicyService,
        usuario_repository: UsuarioRepositoryProtocol
    ):
        self.settings = settings
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.password_service = password_service
        self.mail_service = mail_service
        self.image_service = image_service
        self.password_policy = password_policy
        self.mail_policy = mail_policy
        self.usuario_repository = usuario_repository
    @property
    def register_use_case(self) -> RegisterUseCase:

        return RegisterUseCase(
            settings=self.settings,
            auth_user_repository=self.auth_user_repository,
            password_service=self.password_service,
            password_policy=self.password_policy,
            mail_service=self.mail_service,
            image_service=self.image_service,
            token_service=self.token_service,
            mail_policy=self.mail_policy,
            usuario_repository=self.usuario_repository
        )

        
class ContainerLogin:
    def __init__(
        self,
        settings: Settings,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol,
        cookies_service: CookiesService,
        user_validation_service: UserValidationService,
        token_repository: TokenRepositoryProtocol
    ):
        self.settings = settings
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.password_service = password_service
        self.cookies_service = cookies_service
        self.user_validation_service = user_validation_service
        self.token_repository = token_repository
        

    @property
    def login_use_case(self) -> LoginUseCase:

        return LoginUseCase(
            settings=self.settings,
            auth_user_repository=self.auth_user_repository,
            token_service=self.token_service,
            password_service=self.password_service,
            cookies_service = self.cookies_service,
            user_validation_service = self.user_validation_service,
            token_repository = self.token_repository
        )

class ContainerVerifyMail:
    def __init__(
        self,
        settings: Settings,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        cookies_service: CookiesService
    ):
        self.settings = settings
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.cookies_service = cookies_service
    @property
    def verify_mail_use_case(self) -> VerifyMailUseCase:

        return VerifyMailUseCase(
            auth_user_repository=self.auth_user_repository,
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