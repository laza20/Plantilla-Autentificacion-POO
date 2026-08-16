from src.main import app
from src.test.presentation.web.overrides.override_refresh_token import crear_override
from src.container.providers import get_refresh_token_service
from src.config.config import settings


def test_debe_refrescar_el_token_correctamente(test_client):
    app.dependency_overrides[get_refresh_token_service] = crear_override()

    test_client.cookies.set("refresh_token", "un_token_valido")
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/Refresh/Token",
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Access token renovado"