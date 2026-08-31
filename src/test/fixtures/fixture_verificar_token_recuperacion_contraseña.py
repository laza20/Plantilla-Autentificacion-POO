from src.test.unit.auth.domain.service import (
    stub_token_service
)
from src.test.unit.auth.domain.fakes.fake_recuperar_contraseña_repository import FakeRecuperarContraseñaRepository
from src.auth.application.use_cases.recover_password.solicitud_recuperacion import SolicitudRecuperacionUseCase

class VerificarTokenRecuperacionContraseñaTestEnvironment:
    def __init__(self):
        self.recuperar_contraseña_repository = FakeRecuperarContraseñaRepository()
        self.token_service = stub_token_service.StubTokenService()
    def use_case(self):
        return SolicitudRecuperacionUseCase(
            recuperar_contraseña_repository = self.recuperar_contraseña_repository,
            token_service = self.token_service
        )