from test.presentation.web.stub.stub_logout import StubLogoutUseCase

def crear_override(*, resultado=None, excepcion=None):
    def override_logout_use_case():
        stub = StubLogoutUseCase()
        stub.resultado_a_devolver = resultado
        stub.excepcion_a_lanzar = excepcion
        return stub
    return override_logout_use_case