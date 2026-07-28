from src.auth.application.use_cases.logout import LogoutUseCase
from test.unit.auth.domain.service import stub_cookies_service

class LogoutTestEnvironment:
    def __init__(self):
        self.cookies_service = stub_cookies_service.StubCookiesService()
    def use_case(self):
        return LogoutUseCase(
            cookies_service = self.cookies_service
        )