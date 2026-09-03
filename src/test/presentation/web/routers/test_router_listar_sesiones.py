import pytest
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_listar_sesiones import StubListarSesionesUseCase
from src.test.presentation.web.stub.stub_current_user import StubCurrentUserUseCase
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.container.providers import get_user_validation_service, get_listar_sesiones_use_case
from src.auth.presentation.web.guards import get_current_user
from fastapi import status
from src.config.config import settings
from src.main import app


def test_debe_listar_sesiones(test_client):
    usuario = AuthUser(
        id_usuario=1,
        email="test@test.com",
        password="password@123"
    )

    sesiones = {
        "id_sesion":1,
        "hash_refresh_token":"hash_refresh_token_1",
        "ip": "localhost",
        "id_usuario": 1
    }
    app.dependency_overrides[get_current_user] = lambda: {"id_usuario": 1, "email": "test@test.com"}
    app.dependency_overrides[get_user_validation_service] = crear_override(
        stub_class=StubCurrentUserUseCase, 
        resultado=usuario
        )

    app.dependency_overrides[get_listar_sesiones_use_case] = crear_override(
        stub_class=StubListarSesionesUseCase,
        resultado=sesiones
    )

    response = test_client.get(
        f"/{settings.NOMBRE_APP}/usuarios/listar_sesiones"
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id_sesion"] == sesiones["id_sesion"]
    assert data["hash_refresh_token"] == sesiones["hash_refresh_token"]
    assert data["ip"] == sesiones["ip"]
    assert data["id_usuario"] == sesiones["id_usuario"]