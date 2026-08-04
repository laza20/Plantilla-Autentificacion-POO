from src.test.unit.auth.domain.service import (
    stub_password_service,
    stub_token_service
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.login import LoginUseCase
from src.test.config.config import TestSettings
from test.unit.auth.domain.service import stub_cookies_service
from src.auth.domain.services.user_validation_service import UserValidationService


class LoginTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.password_service = stub_password_service.StubPasswordService()
        self.token_service = stub_token_service.StubTokenService()
        self.settings = TestSettings()
        self.cookies_service = stub_cookies_service.StubCookiesService()
        self.user_validation_service = UserValidationService(            
            auth_user_repository=self.auth_user_repository,
            settings=self.settings)

    def use_case(self):
        return LoginUseCase(
            auth_user_repository=self.auth_user_repository,
            password_service=self.password_service,
            token_service=self.token_service,
            settings=self.settings,
            cookies_service = self.cookies_service,
            user_validation_service = self.user_validation_service
        )