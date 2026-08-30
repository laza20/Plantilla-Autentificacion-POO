from src.test.unit.auth.domain.service import stub_token_service
from src.auth.application.use_cases.refresh_token import RefreshTokenUseCase


class RefreshTokenTestEnvironment:
    def __init__(self):
        self.token_service = stub_token_service.StubTokenService()
    def use_case(self):
        return RefreshTokenUseCase(
            token_service = self.token_service
        )