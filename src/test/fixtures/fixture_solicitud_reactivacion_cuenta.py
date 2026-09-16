from src.test.unit.auth.domain.service import (stub_mail_service, stub_token_service)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.reactivacion_cuenta.solicitud_reactivacion_cuenta import EnviarMailReactivacionUseCase
from src.test.config.config import TestSettings
from src.test.unit.auth.domain.service import stub_mail_policy_service


class SolicitudReactivacionCuentaTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_policy = stub_mail_policy_service.StubMailPolicy()
        self.settings = TestSettings()

    def use_case(self):
        return EnviarMailReactivacionUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            token_service=self.token_service,
            mail_policy=self.mail_policy,
            settings=self.settings
        )