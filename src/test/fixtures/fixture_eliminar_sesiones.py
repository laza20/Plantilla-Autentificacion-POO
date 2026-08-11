from src.test.unit.auth.domain.fakes.fake_token_repository import FakeSesionRepository
from src.auth.application.use_cases.eliminar_sesiones import EliminarSesionesUseCase


class EliminarSesionesEnvironment:
    def __init__(self):
        self.token_repository= FakeSesionRepository()

    def use_case(self):
        return EliminarSesionesUseCase(
            token_repository=self.token_repository
        )
                 
