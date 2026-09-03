from src.test.unit.auth.domain.service import (
    stub_password_service,
    stub_token_service
)
from fastapi import Response, Request
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.test.unit.auth.domain.fakes.fake_sesion_repository import FakeSesionRepository
from src.auth.application.use_cases.login import LoginUseCase
from src.test.config.config import TestSettings
from src.auth.domain.services.user_validation_service import UserValidationService


class LoginTestEnvironment:

    def __init__(self):
        self.request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/login",
                "headers": [
                    (b"user-agent", b"pytest"),
                ],
                "client": ("127.0.0.1", 50000),
            }
        )
        self.auth_user_repository = FakeUserRepository()
        self.token_service = stub_token_service.StubTokenService()
        self.password_service = stub_password_service.StubPasswordService()
        self.user_validation_service = UserValidationService(            
            auth_user_repository=self.auth_user_repository,
            settings=TestSettings())
        self.sesion_repository = FakeSesionRepository()

    def use_case(self):
        return LoginUseCase(
            auth_user_repository=self.auth_user_repository,
            token_service=self.token_service,
            password_service=self.password_service,
            user_validation_service = self.user_validation_service,
            sesion_repository = self.sesion_repository
        )


    