from src.test.unit.auth.domain.service import (
    stub_mail_service,
    stub_token_service,
    stub_auth_mail_content
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.reenviar_mail import ReenviarMailUseCase
from src.test.config.config import TestSettings
from src.test.unit.auth.domain.service import stub_mail_policy_service


class ReenviarMailTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.mail_content = stub_auth_mail_content.StubAuthMailContent()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_policy = stub_mail_policy_service.StubMailPolicy()
        self.settings = TestSettings()

    def use_case(self):
        return ReenviarMailUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            mail_content = self.mail_content,
            token_service=self.token_service,
            mail_policy=self.mail_policy,
            settings=self.settings
        )