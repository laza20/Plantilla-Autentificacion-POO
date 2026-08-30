from src.auth.application.use_cases.logout import LogoutUseCase
from test.unit.auth.domain.service import stub_token_service
from test.unit.auth.domain.fakes import fake_token_repository

class LogoutTestEnvironment:
    def __init__(self):
        self.token_service = stub_token_service.StubTokenService()
        self.token_repository = fake_token_repository.FakeSesionRepository()
    def use_case(self):
        return LogoutUseCase(
            token_service = self.token_service,
            token_repository = self.token_repository
        )