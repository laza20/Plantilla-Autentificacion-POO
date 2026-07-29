from src.test.unit.auth.domain.service import stub_token_service
from src.test.unit.auth.domain.fakes.fake_user_repository import FakeUserRepository
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.test.config.config import TestSettings
from test.unit.auth.domain.service import stub_cookies_service


class VerifyEmailTestEnvironment:

    def __init__(self):
        self.user_repository = FakeUserRepository()
        self.token_service = stub_token_service.StubTokenService()
        self.settings = TestSettings()
        self.cookies_service = stub_cookies_service.StubCookiesService()

    def use_case(self):
        return VerifyMailUseCase(
            user_repository=self.user_repository,
            token_service=self.token_service,
            settings=self.settings,
            cookies_service = self.cookies_service
        )