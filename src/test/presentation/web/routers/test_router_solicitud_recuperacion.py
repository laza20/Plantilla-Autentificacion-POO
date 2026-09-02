from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_solicitud_recuperacion import StubSolicitudRecuperacionUseCase
from src.auth.infrastructure.persistence.postgres.schemas.schemas_recepcion import SolicitudRecuperacionRequest
from fastapi import status
from src.container.providers import get_solicitud_recuperacion_contraseña_use_case
from src.config.config import settings


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