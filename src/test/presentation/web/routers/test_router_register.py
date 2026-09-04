from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_register_router import StubRegisterUseCase
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import (
    MailRepetido, LongitudExcedida, ContraseñaNoSegura,
    LimiteTamañoSuperado, ExtensionNoPermitida, ErrorCloudinary,
    SinCargas
    )
from fastapi import status
from src.container.providers import get_register_use_case
from src.config.config import settings
import pytest
from io import BytesIO

def test_register_crear_correctamente(test_client):
    usuario_retorno = AuthUser(
            **{
                "email": "test@test.com",
                "password": "password@123",
            }
        )
    app.dependency_overrides[get_register_use_case] = crear_override(stub_class=StubRegisterUseCase, resultado=usuario_retorno)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/registrar",
        data={            
            "email": "test@test.com",
            "password": "password@123"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json()["email"] == "test@test.com"
    assert response.json()["imagen_url"] is None
    assert response.json()["created_at"] is None
    assert response.json()["is_verified"] is False
    assert "password" not in response.json()

@pytest.mark.parametrize(
    "exception",
    [
        SinCargas(),
        MailRepetido(),
        LongitudExcedida(),
        ContraseñaNoSegura(),
        LimiteTamañoSuperado(),
        ExtensionNoPermitida(),
        ErrorCloudinary("Error 505")
    ],
    ids=lambda exception: type(exception).__name__
)
def test_debe_lanzar_excepciones(test_client, exception):

    app.dependency_overrides[get_register_use_case] = crear_override(stub_class=StubRegisterUseCase, excepcion=exception)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/registrar",
        data={            
            "email": "test@test.com",
            "password": "password@123"}
    )

    assert response.status_code == exception.status_code
    assert "email" not in response.json()


def test_debe_dar_error_por_datos_mal_enviados(test_client):
    app.dependency_overrides[get_register_use_case] = crear_override(stub_class=StubRegisterUseCase, excepcion=status.HTTP_422_UNPROCESSABLE_CONTENT)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/registrar",
        data={            
            "mail": "test@test.com",
            "password": "password@123"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_debe_registrar_correctamente_con_imagen(test_client):
    usuario_retorno = AuthUser(
            **{
                "email": "test@test.com",
                "password": "password@123",
                "imagen_url": "https://res.cloudinary.com/demo/image/upload/foto.jpg"
            }
        )
    app.dependency_overrides[get_register_use_case] = crear_override(stub_class=StubRegisterUseCase, resultado=usuario_retorno)
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/registrar",
        data={
            "email": "test@test.com",
            "password": "password@123",
        },
        files={
            "imagen": (
                "foto.jpg",
                BytesIO(b"contenido falso de una imagen"),
                "image/jpeg",
            )
        }
    )

    assert response.json()["imagen_url"] == "https://res.cloudinary.com/demo/image/upload/foto.jpg"