import pytest
from test.auth.presentation.web.overrides.override_crear import crear_override
from test.auth.presentation.web.stub.stub_eliminar_sesion import StubEliminarSesionesUseCase
from test.auth.presentation.web.stub.stub_current_user import StubCurrentUserUseCase
from src.auth.domain.entities.entitie_auth_users import AuthUser
from src.container.auth.providers import get_user_validation_service, get_eliminar_sesiones_use_case, get_current_user
from fastapi import status
from src.config.config import settings
from main import app

id_sesion = 1
def test_eliminar_sesion(test_client):
    usuario = AuthUser(
        id_usuario=1,
        email="test@test.com",
        password="password@123"
    )

    sesion_resultado = {"message": "Sesión eliminada"}
    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_user_validation_service] = crear_override(
        stub_class=StubCurrentUserUseCase, 
        resultado=usuario
        )

    app.dependency_overrides[get_eliminar_sesiones_use_case] = crear_override(
        stub_class=StubEliminarSesionesUseCase,
        resultado=sesion_resultado
    )

    response = test_client.delete(
        f"/{settings.NOMBRE_APP}/usuarios/eliminar_sesion/{id_sesion}"
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["message"] == sesion_resultado["message"]


def test_no_se_encontro_la_sesion_a_eliminar(test_client):
    usuario = AuthUser(
        id_usuario=1,
        email="test@test.com",
        password="password@123"
    )

    sesion_resultado = {"message": "La sesion que se quiso eliminar, no pudo ser encontrada"}
    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_user_validation_service] = crear_override(
        stub_class=StubCurrentUserUseCase, 
        resultado=usuario
        )

    app.dependency_overrides[get_eliminar_sesiones_use_case] = crear_override(
        stub_class=StubEliminarSesionesUseCase,
        resultado=sesion_resultado
    )

    response = test_client.delete(
        f"/{settings.NOMBRE_APP}/usuarios/eliminar_sesion/{5}"
    )

    data = response.json()
    assert data["message"] == sesion_resultado["message"]