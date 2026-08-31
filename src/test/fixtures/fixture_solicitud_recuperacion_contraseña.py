from src.test.unit.auth.domain.service import (
    stub_image_service,
    stub_mail_service,
    stub_password_service,
    stub_token_service,
    stub_unit_of_work
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.test.unit.auth.domain.fakes.fake_recuperar_contraseña_repository import FakeRecuperarContraseñaRepository
from src.auth.application.use_cases.recover_password.solicitud_recuperacion import SolicitudRecuperacionUseCase
from src.test.config.config import TestSettings


class SolicitudRecuperacionContraseñaTestEnvironment:

    def __init__(self):
        self.recuperar_contraseña_repository = FakeRecuperarContraseñaRepository()
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.token_service = stub_token_service.StubTokenService()
        self.settings = TestSettings()

    def use_case(self):
        return SolicitudRecuperacionUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            unit_of_work_service = self.unit_of_work_service,
            auth_user_repository = self.auth_user_repository,
            mail_service = self.mail_service,
            token_service = self.token_service,
            settings = self.settings
        )