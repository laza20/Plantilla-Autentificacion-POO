from src.test.unit.auth.domain.service import (stub_mail_service, stub_token_service)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.eliminar_usuario.solicitud_eliminar_usuario import SolicitudEliminacionUsuarioUseCase
from src.test.config.config import TestSettings
from src.test.unit.auth.domain.service import stub_mail_policy_service


class SolicitudEliminacionUsuarioTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.token_service = stub_token_service.StubTokenService()
        self.settings = TestSettings()

    def use_case(self):
        return SolicitudEliminacionUsuarioUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            token_service=self.token_service,
            settings=self.settings
        )