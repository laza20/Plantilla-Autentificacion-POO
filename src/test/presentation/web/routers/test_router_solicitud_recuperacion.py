from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_solicitud_recuperacion import StubSolicitudRecuperacionUseCase
from src.auth.infrastructure.persistence.postgres.schemas.schemas_recepcion import SolicitudRecuperacionRequest
from fastapi import status
from src.container.providers import get_solicitud_recuperacion_contraseña_use_case
from src.config.config import settings
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError
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
    "exception",
    [
        UsuarioNoEncontrado("Usuario no encontrado en la base de datos"), 
        UsuarioError("No se pudo registrar la solicitud de recuperación.")
    ],
    ids=lambda exception: type(exception).__name__
)
def test_debe_transmitir_excepciones(test_client, exception):
    app.dependency_overrides[get_solicitud_recuperacion_contraseña_use_case] = crear_override(stub_class=StubSolicitudRecuperacionUseCase, excepcion=exception)

    response = test_client.post(
        f"/{settings.NOMBRE_APP}/usuarios/solicitud/recuperacion",
        json={            
            "email": "test@test.com"
        }
    )

    data = response.json()
    assert response.status_code == exception.status_code
    assert data["detail"] == exception.message