from src.test.unit.auth.domain.service import (
    stub_token_service, stub_unit_of_work
    )
from src.test.unit.auth.domain.fakes.fake_sesion_repository import FakeSesionRepository
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.eliminar_usuario.eliminar_usuario import EliminarUsuarioUseCase



class EliminarUsuarioTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.token_service = stub_token_service.StubTokenService()
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()
        self.sesion_repository = FakeSesionRepository()

    def use_case(self):
        return EliminarUsuarioUseCase(
            auth_user_repository = self.auth_user_repository,
            token_service = self.token_service,
            unit_of_work_service = self.unit_of_work_service,
            sesion_repository = self.sesion_repository
        )