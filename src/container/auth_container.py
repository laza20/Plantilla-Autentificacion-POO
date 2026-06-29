from src.config.config import Settings
from src.auth.utils.usuarios_utils import UserMapper
from src.auth.domain.protocols.user_repository import UserRepositoryProtocol
from src.auth.domain.protocols.token_service import TokenProtocol
from src.auth.domain.protocols.password_service import PasswordProtocol
from src.auth.domain.protocols.mail_service import MailProtocol
from src.auth.domain.protocols.image_service import ImageProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.use_cases.register import RegisterUseCase


class AuthContainer:

    def __init__(
        self,
        settings: Settings,
        repository: UserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol, 
        mail_service: MailProtocol,        
        image_service: ImageProtocol,
        password_policy: PasswordPolicyService,
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
