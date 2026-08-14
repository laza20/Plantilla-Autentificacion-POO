from src.test.presentation.web.stub.stub_register_router import StubRegisterUseCase

def crear_override(*, resultado=None, excepcion=None):
    def override_register_use_case():
        stub = StubRegisterUseCase()
        stub.resultado_a_devolver = resultado
        stub.excepcion_a_lanzar = excepcion
        return stub
    return override_register_use_case