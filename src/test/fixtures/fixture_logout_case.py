from src.auth.application.use_cases.logout import LogoutUseCase
from src.test.unit.auth.domain.service import stub_token_service
from src.test.unit.auth.domain.fakes import fake_sesion_repository

class LogoutTestEnvironment:
    def __init__(self):
        self.token_service = stub_token_service.StubTokenService()
        self.sesion_repository = fake_sesion_repository.FakeSesionRepository()
    def use_case(self):
        return LogoutUseCase(
            token_service = self.token_service,
            sesion_repository = self.sesion_repository
        )