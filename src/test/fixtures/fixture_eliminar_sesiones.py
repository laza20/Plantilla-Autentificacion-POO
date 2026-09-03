from src.test.unit.auth.domain.fakes.fake_sesion_repository import FakeSesionRepository
from src.auth.application.use_cases.eliminar_sesiones import EliminarSesionesUseCase


class EliminarSesionesEnvironment:
    def __init__(self):
        self.sesion_repository= FakeSesionRepository()

    def use_case(self):
        return EliminarSesionesUseCase(
            sesion_repository=self.sesion_repository
        )
                 
