from src.test.presentation.web.stub.stub_refresh_token import StubRefreshTokenUseCase

def crear_override(*, resultado=None, excepcion=None):
    def override_refresh_token_use_case():
        stub = StubRefreshTokenUseCase()
        stub.resultado_a_devolver = resultado
        stub.excepcion_a_lanzar = excepcion
        return stub
    return override_refresh_token_use_case