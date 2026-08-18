import pytest
from test.presentation.web.overrides.override_crear import crear_override
from test.presentation.web.stub.stub_login import StubLoginUseCase
from src.auth.infrastructure.persistence.postgres.models_auth_users import LoginResponse, UsuarioLogeado, UserTokens
from src.container.providers import get_login_use_case
from fastapi import status
from src.config.config import settings
from src.main import app

def test_logear_usuario_correctamente(test_client):
    usuario = UsuarioLogeado(
        email="test@test.com"
    )
    token = UserTokens(
        access_token="access_token_1",
        refresh_token="refresh_token_1"
    )

    usuario_logeado = LoginResponse(
        tokens=token,
        usuario=usuario
    )
    
    app.dependency_overrides[get_login_use_case] = crear_override(
        stub_class=StubLoginUseCase, 
        resultado=usuario_logeado
        )

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/login",
        data={
            "username": "test@test.com",
            "password": "password@123"
        },
        headers={
            "User-Agent": "pytest"
        }
    )

    data = response.json()

    assert data["tokens"]["access_token"] == usuario_logeado.tokens.access_token
    assert data["tokens"]["refresh_token"] == usuario_logeado.tokens.refresh_token
    assert data["tokens"]["token_type"] == "bearer"
    assert data["usuario"]["email"] == usuario_logeado.usuario.email
    assert data["usuario"]["imagen_url"] == usuario_logeado.usuario.imagen_url


def test_verificar_que_el_logeo_correcto_devuelva_un_status_correcto(test_client):
    usuario = UsuarioLogeado(
        email="test@test.com"
    )
    token = UserTokens(
        access_token="access_token_1",
        refresh_token="refresh_token_1"
    )

    usuario_logeado = LoginResponse(
        tokens=token,
        usuario=usuario
    )
    
    app.dependency_overrides[get_login_use_case] = crear_override(
        stub_class=StubLoginUseCase, 
        resultado=usuario_logeado
        )

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/login",
        data={
            "username": "test@test.com",
            "password": "password@123"
        },
        headers={
            "User-Agent": "pytest"
        }
    )

    assert response.status_code == status.HTTP_202_ACCEPTED