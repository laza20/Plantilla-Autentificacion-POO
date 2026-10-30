import pytest
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_current_user import StubCurrentUserUseCase
from src.auth.domain.entities.entitie_auth_users import UsuarioCreado
from src.container.auth.providers import get_user_validation_service, get_current_user
from fastapi import status
from src.config.config import settings
from src.main import app


def test_ver_usuario_correctamente(test_client):
    usuario_esperado = UsuarioCreado(
            **{
                "id_usuario":1,
                "email": "test@test.com"
            }
        )

    app.dependency_overrides[get_current_user] = lambda: {"id_usuario": 1, "email": "test@test.com"}
    app.dependency_overrides[get_user_validation_service] = crear_override(
        stub_class=StubCurrentUserUseCase, 
        resultado=usuario_esperado
        )

    response = test_client.get(f"/{settings.NOMBRE_APP}/usuarios/user/current")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == usuario_esperado.email


def test_debe_error_si_el_usuario_no_esta_autenticado(test_client):

    app.dependency_overrides[get_user_validation_service] = crear_override(
        stub_class=StubCurrentUserUseCase
        )

    response = test_client.get(f"/{settings.NOMBRE_APP}/usuarios/user/current")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED