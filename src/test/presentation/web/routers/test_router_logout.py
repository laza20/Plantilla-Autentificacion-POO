import pytest
from test.presentation.web.overrides.override_crear import crear_override
from test.presentation.web.stub.stub_logout import StubLogoutUseCase
from src.container.providers import get_logout_service
from src.config.config import settings
from src.main import app



def test_debe_eliminar_la_sesion(test_client):
    app.dependency_overrides[get_logout_service] = crear_override(stub_class=StubLogoutUseCase)

    test_client.cookies.set("refresh_token", "un_token_valido")
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/Logout",
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Sesión cerrada"