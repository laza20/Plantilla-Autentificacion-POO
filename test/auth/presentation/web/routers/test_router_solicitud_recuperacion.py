from main import app
from test.auth.presentation.web.overrides.override_crear import crear_override
from test.auth.presentation.web.stub.stub_solicitud_recuperacion import StubSolicitudRecuperacionUseCase
from fastapi import status
from auth_core.container.auth.providers import get_solicitud_recuperacion_contraseña_use_case
from auth_core.config.config import settings
from auth_core.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError
import pytest

def test_solicitud_recuperacion_correctamente(test_client):
    resultado = {
                "message": 
                "Mail enviado correctamente, revise su bandeja de entrada, si no lo encuentra revise en spam o correos no deseados."
    }
    app.dependency_overrides[get_solicitud_recuperacion_contraseña_use_case] = crear_override(stub_class=StubSolicitudRecuperacionUseCase, resultado=resultado)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/solicitud/recuperacion",
        json={            
            "email": "test@test.com"}
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["message"] == resultado["message"]



@pytest.mark.parametrize(
    "exception, expected_status",
    [
        (
            UsuarioNoEncontrado("Usuario no encontrado en la base de datos"),
            status.HTTP_409_CONFLICT
        ),
        (
            UsuarioError("No se pudo registrar la solicitud de recuperación."),
            status.HTTP_400_BAD_REQUEST
        ),
    ],
    ids=lambda value: type(value).__name__
)
def test_debe_transmitir_excepciones(test_client, exception, expected_status):
    app.dependency_overrides[get_solicitud_recuperacion_contraseña_use_case] = crear_override(stub_class=StubSolicitudRecuperacionUseCase, excepcion=exception)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/solicitud/recuperacion",
        json={            
            "email": "test@test.com"
        }
    )

    data = response.json()
    assert response.status_code == expected_status
    assert data["detail"] == exception.message


def test_debe_verificar_que_se_el_funcionamiento_en_caso_de_no_enviar_bien_el_email(test_client):
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/solicitud/recuperacion",
        json={            
            "mail": "test@test.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_debe_dar_error_por_dato_incorrecto(test_client):
    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/solicitud/recuperacion",
        json={            
            "email": "test.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT