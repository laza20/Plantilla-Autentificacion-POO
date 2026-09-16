from src.test.unit.auth.domain.service import (
    stub_token_service, stub_unit_of_work
    )
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.reactivacion_cuenta.reactivar_cuenta import ReactivarUsuarioUseCase
from src.test.config.config import TestSettings

class ReactivarCuentaTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.token_service = stub_token_service.StubTokenService()
        self.settings = TestSettings()
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()

    def use_case(self):
        return ReactivarUsuarioUseCase(
            auth_user_repository = self.auth_user_repository,
            token_service = self.token_service,
            settings = self.settings,
            unit_of_work_service = self.unit_of_work_service
        )