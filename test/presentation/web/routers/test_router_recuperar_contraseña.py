from main import app
from test.presentation.web.overrides.override_crear import crear_override
from test.presentation.web.stub.stub_recuperar_contraseña import StubRecuperarContraseñaUseCase
from fastapi import status
from src.container.auth.providers import get_recuperar_contraseña_use_case, get_token_service
from src.config.config import settings
from src.auth.domain.exceptions.tokens import TokenNoDesactivado
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoModificado, UsuarioNoEncontrado
from src.domain.exceptions.domain import ErrorCreacion
import pytest


def test_debe_verificar_que_el_retorno_sea_correcto_en_el_caso_positivo(test_client):
    resultado = {"message": "La contraseña fue modificada correctamente."}
    app.dependency_overrides[get_recuperar_contraseña_use_case] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        resultado=resultado
        )
    app.dependency_overrides[get_token_service] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        resultado={"reset_token": "un_token_valido"}
    )

    test_client.cookies.set("reset_token", "un_token_valido")
    response = test_client.patch(
        f"/{settings.NOMBRE_APP}/usuarios/modificar/password",
        json={            
            "password": "Boca1234@"} #contraseña nueva
    )

    data = response.json()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert data["message"] == 'La contraseña fue modificada correctamente.'


@pytest.mark.parametrize(
    "exception, expected_status",
    [
        (
            TokenNoDesactivado("El token no pudo ser desactivado"),
            status.HTTP_409_CONFLICT
        ),
        (
            UsuarioNoModificado("La contraseña no pudo ser modificada."),
            status.HTTP_409_CONFLICT
        ),
        (
            UsuarioNoEncontrado("Usuario no encontrado en la base de datos."),
            status.HTTP_409_CONFLICT
        ),
        (
            ErrorCreacion("Error al crear el registro en la base de datos."),
            status.HTTP_409_CONFLICT
        ),
    ],
    ids=lambda value: type(value).__name__
)
def test_debe_verificar_que_se_produce_una_excepcion_si_algo_falla(test_client, exception, expected_status):
    app.dependency_overrides[get_recuperar_contraseña_use_case] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        excepcion=exception
    )
    app.dependency_overrides[get_token_service] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        resultado={"reset_token": "un_token_valido"}
    )

    test_client.cookies.set("reset_token", "un_token_valido")
    response = test_client.patch(
        f"/{settings.NOMBRE_APP}/usuarios/modificar/password",
        json={            
            "password": "Boca1234@"} #contraseña nueva
    )

    assert response.status_code == expected_status
    assert response.json()["detail"] == exception.message