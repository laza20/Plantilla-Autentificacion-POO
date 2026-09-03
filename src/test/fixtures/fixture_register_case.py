from src.test.unit.auth.domain.service import (
    stub_image_service,
    stub_mail_service,
    stub_password_service,
    stub_token_service
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.test.unit.auth.domain.fakes.fake_usuario_repository import FakeUsuarioRepository
from src.auth.application.use_cases.register import RegisterUseCase
from src.test.config.config import TestSettings
from src.test.unit.auth.domain.service import stub_password_policy_service
from src.test.unit.auth.domain.service import stub_mail_policy_service


class RegisterTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.password_service = stub_password_service.StubPasswordService()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_service = stub_mail_service.StubMailService()
        self.image_service = stub_image_service.StubImageService()
        self.password_policy = stub_password_policy_service.StubPasswordPolicy()
        self.mail_policy = stub_mail_policy_service.StubMailPolicy()
        self.settings = TestSettings()
        self.usuario_repository = FakeUsuarioRepository()

    def use_case(self):
        return RegisterUseCase(
            auth_user_repository=self.auth_user_repository,
            password_service=self.password_service,
            mail_service=self.mail_service,
            image_service=self.image_service,
            token_service=self.token_service,
            password_policy=self.password_policy,
            mail_policy=self.mail_policy,
            settings=self.settings,
            usuario_repository=self.usuario_repository
        )