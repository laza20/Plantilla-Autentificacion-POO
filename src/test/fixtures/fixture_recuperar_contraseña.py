from src.test.unit.auth.domain.service import (
    stub_password_service,
    stub_unit_of_work,
    stub_password_policy_service
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.test.unit.auth.domain.fakes.fake_recuperar_contraseña_repository import FakeRecuperarContraseñaRepository
from src.test.unit.auth.domain.fakes.fake_history_password_repository import FakeHistoryPasswordRepository
from src.auth.application.use_cases.recover_password.recuperar_contraseña import RecuperarContraseñaUseCase


class RecuperarContraseñaTestEnvironment:

    def __init__(self):
        self.recuperar_contraseña_repository = FakeRecuperarContraseñaRepository()
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()
        self.password_service = stub_password_service.StubPasswordService()
        self.history_contraseña_repository = FakeHistoryPasswordRepository()
        self.password_policy = stub_password_policy_service.StubPasswordPolicy()
        self.auth_user_repository = FakeUserRepository()

    def use_case(self):
        return RecuperarContraseñaUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            unit_of_work_service = self.unit_of_work_service,
            password_service = self.password_service,
            history_contraseña_repository = self.history_contraseña_repository,
            password_policy = self.password_policy,
            auth_user_repository = self.auth_user_repository
        )