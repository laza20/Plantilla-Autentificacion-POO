from src.main import app
from src.test.presentation.web.overrides.override_verify_mail import crear_override
from src.container.providers import get_verify_mail_use_case
from src.config.config import settings
from src.auth.domain.exceptions.tokens import TokenInvalido, VerificacionInvalida
import pytest

token = "token_correcto_1"

def test_debe_verificar_de_manera_correcta_un_mail(test_client):

    app.dependency_overrides[get_verify_mail_use_case] = crear_override()

    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/verificar/{token}"
    )

    assert response.json()["status"] == "success"
    assert response.json()["message"] == "¡Cuenta activada con éxito!"


def test_debe_lanzar_error_si_el_token_es_invalido(test_client):
    app.dependency_overrides[get_verify_mail_use_case] = crear_override(
        excepcion=TokenInvalido()
    )

    response = test_client.get(f"/{settings.NOMBRE_APP}/usuarios/verificar/token_invalido")

    assert response.status_code == TokenInvalido().status_code
    assert response.json()["detail"] == 'Token de ingreso invalido.'
