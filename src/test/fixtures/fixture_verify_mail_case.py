from src.test.unit.auth.domain.service import stub_token_service
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.verify_email import VerifyMailUseCase
from src.test.config.config import TestSettings


class VerifyEmailTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.token_service = stub_token_service.StubTokenService()

    def use_case(self):
        return VerifyMailUseCase(
            auth_user_repository=self.auth_user_repository,
            token_service=self.token_service
        )