from main import app
from test.auth.presentation.web.overrides.override_crear import crear_override
from test.auth.presentation.web.stub.stub_verify_mail import StubVerifyMailUseCase
from src.auth_core.container.auth.providers import get_verify_mail_use_case
from src.auth_core.config.config import settings
from src.auth_core.auth.domain.exceptions.tokens import TokenInvalido
from fastapi import status

token = "token_correcto_1"

def test_debe_verificar_de_manera_correcta_un_mail(test_client):

    app.dependency_overrides[get_verify_mail_use_case] = crear_override(stub_class=StubVerifyMailUseCase)

    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/verificar/{token}"
    )

    assert response.json()["status"] == "success"
    assert response.json()["message"] == "¡Cuenta activada con éxito!"


def test_debe_lanzar_error_si_el_token_es_invalido(test_client):
    app.dependency_overrides[get_verify_mail_use_case] = crear_override(
        stub_class=StubVerifyMailUseCase,
        excepcion=TokenInvalido()
    )

    response = test_client.get(f"/{settings.NOMBRE_APP}/usuarios/verificar/token_invalido")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
