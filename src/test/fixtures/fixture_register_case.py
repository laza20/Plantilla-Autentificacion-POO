from src.test.unit.auth.domain.service import (
    stub_image_service,
    stub_mail_service,
    stub_password_service,
    stub_token_service
)
from src.test.unit.auth.domain.fakes.fake_user_repository import FakeUserRepository
from src.auth.application.use_cases.register import RegisterUseCase
from src.test.config.config import TestSettings
from test.unit.auth.domain.service import stub_password_policy_service


class RegisterTestEnvironment:

    def __init__(self):
        self.user_repository = FakeUserRepository()
        self.password_service = stub_password_service.StubPasswordService()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_service = stub_mail_service.StubMailService()
        self.image_service = stub_image_service.StubImageService()
        self.password_policy = stub_password_policy_service.StubPasswordPolicy()
        self.settings = TestSettings()

    def use_case(self):
        return RegisterUseCase(
            user_repository=self.user_repository,
            password_service=self.password_service,
            mail_service=self.mail_service,
            image_service=self.image_service,
            token_service=self.token_service,
            password_policy=self.password_policy,
            settings=self.settings,
        )