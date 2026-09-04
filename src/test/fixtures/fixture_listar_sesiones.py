from src.test.unit.auth.domain.fakes.fake_sesion_repository import FakeSesionRepository
from src.auth.application.use_cases.sesiones.listar_sesiones import ListarSesionesUseCase

class ListarSesionesEnvironment:
    def __init__(self):
        self.sesion_repository = FakeSesionRepository()

    def use_case(self):
        return ListarSesionesUseCase(
            sesion_repository=self.sesion_repository
        )