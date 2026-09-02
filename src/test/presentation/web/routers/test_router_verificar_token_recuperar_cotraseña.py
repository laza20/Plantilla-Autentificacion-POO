from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_verificar_token_recuperar_contraseña import StubVerificarTokenRecuperarContraseñaUseCase
from fastapi import status
from src.container.providers import get_verificar_token_recuperacion_contraseña_use_case
from src.config.config import settings
from src.auth.domain.exceptions.tokens import TokenNoVerificado


def test_debe_verificar_el_retorno_del_reset_token_correctamente(test_client):
    token = "un_token_valido"
    token_retorno = "un_nuevo_token"
    app.dependency_overrides[get_verificar_token_recuperacion_contraseña_use_case] = crear_override(
        stub_class=StubVerificarTokenRecuperarContraseñaUseCase,
        resultado=token_retorno
        )

    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/recuperar/password/{token}",
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["message"] == 'Configuracion realizada correctamente.'


def test_debe_verificar_que_el_token_final_es_diferente_al_inicial(test_client):
    token = "un_token_valido"
    token_retorno = "un_nuevo_token"
    app.dependency_overrides[get_verificar_token_recuperacion_contraseña_use_case] = crear_override(
        stub_class=StubVerificarTokenRecuperarContraseñaUseCase,
        resultado=token_retorno
        )

    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/recuperar/password/{token}",
    )

    cookies = response.cookies

    assert cookies["reset_token"] == token_retorno