from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_refresh_token import StubRefreshTokenUseCase
from src.container.providers import get_refresh_token_service
from src.config.config import settings
from src.auth.domain.exceptions.usuarios_exceptions import SinRefreshToken
from src.auth.domain.exceptions.tokens import VerificacionInvalida


def test_debe_refrescar_el_token_correctamente(test_client):
    app.dependency_overrides[get_refresh_token_service] = crear_override(stub_class=StubRefreshTokenUseCase)

    test_client.cookies.set("refresh_token", "un_token_valido")
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/Refresh/Token",
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Access token renovado"


def test_debe_verificar_que_se_produce_una_excepcion_si_no_se_envia_el_refresh_token(test_client):
    app.dependency_overrides[get_refresh_token_service] = crear_override(stub_class=StubRefreshTokenUseCase, excepcion = SinRefreshToken("No hay refresh token en la cookie"))

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/Refresh/Token",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "No hay refresh token en la cookie"


def test_debe_verificar_que_la_verificacion_fue_invalida(test_client):
    app.dependency_overrides[get_refresh_token_service] = crear_override(stub_class=StubRefreshTokenUseCase, excepcion = VerificacionInvalida())

    test_client.cookies.set("refresh_token", "un_token_invalido")
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/Refresh/Token",
    )
    
    assert response.status_code == VerificacionInvalida().status_code
    assert response.json()["detail"] == VerificacionInvalida().message