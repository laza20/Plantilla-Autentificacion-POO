from src.test.presentation.web.stub.stub_verify_mail import StubVerifyMailUseCase

def crear_override(*, resultado=None, excepcion=None):
    def override_verify_mail_use_case():
        stub = StubVerifyMailUseCase()
        stub.resultado_a_devolver = resultado
        stub.excepcion_a_lanzar = excepcion
        return stub
    return override_verify_mail_use_case