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


def test_debe_verificar_la_cookies_se_setean_dentro_del_caso_de_uso(test_client):
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


def test_debe_verificar_que_se_produce_una_excepcion_si_se_envia_el_reset_token_invalido(test_client):
    app.dependency_overrides[get_verificar_token_recuperacion_contraseña_use_case] = crear_override(
        stub_class=StubVerificarTokenRecuperarContraseñaUseCase, 
        excepcion = TokenNoVerificado("Token no verificado")
        )

    token_invalido = "un_token_invalido"
    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/recuperar/password/{token_invalido}",
    )

    data = response.json()

    assert response.status_code == TokenNoVerificado.status_code
    assert data["detail"] == "Token no verificado"


def test_debe_verificar_que_se_produce_una_excepcion_si_no_se_envia_el_reset_token(test_client):
    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/recuperar/password/",
    )

    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Not Found"