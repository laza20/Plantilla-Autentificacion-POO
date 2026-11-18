from main import app
from test.auth.presentation.web.overrides.override_crear import crear_override
from test.auth.presentation.web.stub.stub_register_router import StubRegisterUseCase
from src.auth.application.dtos.auth_user_dto import UsuarioCreado
from src.domain.exceptions.domain import (
    LongitudExcedida, LimiteTamañoSuperado, ExtensionNoPermitida, ErrorCloudinary,
    SinCargas
    )
from src.auth.domain.exceptions.usuarios_exceptions import ContraseñaNoSegura, MailRepetido
from fastapi import status
from src.container.auth.providers import get_register_use_case
from src.config.config import settings
import pytest
from io import BytesIO
from dataclasses import asdict

def test_register_crear_correctamente(test_client):
    usuario_retorno = UsuarioCreado(
            **{
                "id_usuario":1,
                "email": "test@test.com"
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
    "exception, expected_status",
    [
        (
            SinCargas("No se han realizado cargas."),
            status.HTTP_409_CONFLICT
        ),
        (
            MailRepetido("El correo electrónico ya está en uso."),
            status.HTTP_409_CONFLICT
        ),
        (
            LongitudExcedida("Uno o más campos exceden el límite de caracteres permitido."),
            status.HTTP_422_UNPROCESSABLE_CONTENT
        ),
        (
            ContraseñaNoSegura("""La contraseña no cumple con los requisitos de seguridad. Debe contener al menos:        
                - Al menos 8 caracteres
                - Al menos una letra mayúscula
                - Al menos una letra minúscula
                - Al menos un número
                - Al menos un carácter especial"""),
            status.HTTP_400_BAD_REQUEST
        ),
        (
            LimiteTamañoSuperado("El tamaño de la imagen excede el límite permitido."),
            status.HTTP_413_CONTENT_TOO_LARGE
        ),
        (
            ExtensionNoPermitida("La extensión del archivo no está permitida."),
            status.HTTP_400_BAD_REQUEST
        ),
        (
            ErrorCloudinary("Error al subir la imagen a Cloudinary."),
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ],
    ids=lambda value: type(value).__name__
)
def test_debe_lanzar_excepciones(test_client, exception, expected_status):

    app.dependency_overrides[get_register_use_case] = crear_override(stub_class=StubRegisterUseCase, excepcion=exception)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/registrar",
        data={            
            "email": "test@test.com",
            "password": "password@123"}
    )

    assert response.status_code == expected_status
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
    usuario_retorno = UsuarioCreado(
            **{
                "id_usuario":2,
                "email": "test@test.com",
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

    #assert response.json()["imagen_url"] == "https://res.cloudinary.com/demo/image/upload/foto.jpg"