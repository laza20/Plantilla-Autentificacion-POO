from src.config.config import Settings
from src.auth.presentation.web.cookies.cookies import CookiesService
from src.auth.domain.protocols.protocol_auth_user_repository import AuthUserRepositoryProtocol
from src.auth.domain.protocols.protocol_user_repository import UsuarioRepositoryProtocol
from src.auth.domain.protocols.protocol_sesion_repository import TokenRepositoryProtocol
from src.auth.application.use_cases.listar_sesiones import ListarSesionesUseCase
from src.auth.application.use_cases.eliminar_sesiones import EliminarSesionesUseCase
from src.auth.domain.protocols.protocol_token_service import TokenProtocol
from src.auth.domain.protocols.protocol_password_service import PasswordProtocol
from src.auth.domain.protocols.protocol_mail_service import MailProtocol
from src.auth.domain.protocols.protocol_image_service import ImageProtocol
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.auth.application.use_cases.register import RegisterUseCase
from src.auth.application.use_cases.login import LoginUseCase
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.auth.domain.services.user_validation_service import UserValidationService
from src.auth.application.use_cases.logout import LogoutUseCase
from src.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.auth.application.use_cases.recover_password.solicitud_recuperacion import SolicitudRecuperacionUseCase
from src.auth.application.use_cases.recover_password.verificar_token import VerificarTokenUseCase
from src.auth.application.use_cases.recover_password.recuperar_contraseña import RecuperarContraseñaUseCase
from src.auth.domain.services.mail_policy import MailPolicyService
from src.auth.domain.protocols.protocol_recover_password_repository import RecuperarContraseñaProtocol
from src.auth.domain.protocols.protocol_history_password_repository import HistoryRepositoryProtocol
from src.auth.domain.protocols.protocol_unit_of_work import UnitOfWorkProtocol

class ContainerEliminarSesiones:
    def __init__(
        self,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.sesion_repository = sesion_repository
    @property
    def eliminar_sesiones_use_case(self) -> EliminarSesionesUseCase:
        return EliminarSesionesUseCase(
            sesion_repository=self.sesion_repository
            )

class ContainerListarSesiones:
    def __init__(
        self,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.sesion_repository = sesion_repository
    @property
    def listar_sesiones_use_case(self) -> ListarSesionesUseCase:
        return ListarSesionesUseCase(
            sesion_repository=self.sesion_repository
            )


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
        usuario_repository: UsuarioRepositoryProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
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
        self.unit_of_work_service = unit_of_work_service
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
            usuario_repository=self.usuario_repository,
            unit_of_work_service=self.unit_of_work_service
        )

        
class ContainerLogin:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        password_service: PasswordProtocol,
        user_validation_service: UserValidationService,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.password_service = password_service
        self.user_validation_service = user_validation_service
        self.sesion_repository = sesion_repository
        

    @property
    def login_use_case(self) -> LoginUseCase:

        return LoginUseCase(
            auth_user_repository=self.auth_user_repository,
            token_service=self.token_service,
            password_service=self.password_service,
            user_validation_service = self.user_validation_service,
            sesion_repository = self.sesion_repository
        )

class ContainerVerifyMail:
    def __init__(
        self,
        auth_user_repository: AuthUserRepositoryProtocol,
        token_service: TokenProtocol,
        unit_of_work_service: UnitOfWorkProtocol
    ):
        self.auth_user_repository = auth_user_repository
        self.token_service = token_service
        self.unit_of_work_service = unit_of_work_service
    @property
    def verify_mail_use_case(self) -> VerifyMailUseCase:

        return VerifyMailUseCase(
            auth_user_repository=self.auth_user_repository,
            token_service=self.token_service,
            unit_of_work_service=self.unit_of_work_service
        )
    

class ContainerLogout:
    def __init__(
        self,
        token_service: TokenProtocol,
        sesion_repository: TokenRepositoryProtocol
    ):
        self.token_service = token_service
        self.sesion_repository = sesion_repository
    @property
    def logout_use_case(self) -> LogoutUseCase:
        return LogoutUseCase(
            token_service=self.token_service,
            sesion_repository=self.sesion_repository
        )
    
class ContainerRefreshToken:
    def __init__(
        self,
        token_service: TokenProtocol
    ):
        self.token_service = token_service
    @property
    def refresh_token_use_case(self) -> RefreshTokenUseCase:
        return RefreshTokenUseCase(
            token_service = self.token_service
        )



class ContainerSolicitudRecuperacion:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        auth_user_repository: AuthUserRepositoryProtocol,
        mail_service: MailProtocol,
        token_service: TokenProtocol,
        settings: Settings
    ):

        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.unit_of_work_service = unit_of_work_service
        self.auth_user_repository = auth_user_repository
        self.mail_service = mail_service
        self.token_service = token_service
        self.settings = settings

    @property
    def solicitud_recuperacion_use_case(self) -> SolicitudRecuperacionUseCase:

        return SolicitudRecuperacionUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            unit_of_work_service = self.unit_of_work_service,
            auth_user_repository = self.auth_user_repository,
            mail_service = self.mail_service, 
            token_service = self.token_service,
            settings=self.settings
        )


class ContainerVerificarTokenRecuperacion:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        token_service: TokenProtocol,
    ):
        self.recuperar_contraseña_repository = recuperar_contraseña_repository
        self.token_service = token_service

    @property
    def verificar_token_recuperacion_use_case(self) -> VerificarTokenUseCase:
        return VerificarTokenUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            token_service = self.token_service
        )


class ContainerRecuperarContraseña:
    def __init__(
            self,
            recuperar_contraseña_repository: RecuperarContraseñaProtocol,
            unit_of_work_service: UnitOfWorkProtocol,
            password_service: PasswordProtocol,
            history_contraseña_repository: HistoryRepositoryProtocol,
            password_policy : PasswordPolicyService,
            auth_user_repository: AuthUserRepositoryProtocol
        ):
            self.recuperar_contraseña_repository = recuperar_contraseña_repository
            self.unit_of_work_service = unit_of_work_service
            self.password_service = password_service
            self.history_contraseña_repository = history_contraseña_repository
            self.password_policy = password_policy
            self.auth_user_repository = auth_user_repository
    @property
    def recuperar_contraseña_use_case(self) -> RecuperarContraseñaUseCase:
        return RecuperarContraseñaUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            unit_of_work_service = self.unit_of_work_service,
            password_service = self.password_service,
            history_contraseña_repository = self.history_contraseña_repository,
            password_policy = self.password_policy,
            auth_user_repository = self.auth_user_repository
        )