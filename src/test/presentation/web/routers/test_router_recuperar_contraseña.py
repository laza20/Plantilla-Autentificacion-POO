from src.main import app
from src.test.presentation.web.overrides.override_crear import crear_override
from src.test.presentation.web.stub.stub_recuperar_contraseña import StubRecuperarContraseñaUseCase
from fastapi import status
from src.container.providers import get_recuperar_contraseña_use_case, get_token_service
from src.config.config import settings
from src.auth.domain.exceptions.tokens import TokenNoDesactivado
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoModificado, UsuarioNoEncontrado
from src.auth.domain.exceptions.domain import ErrorCreacion


def test_debe_verificar_que_el_retorno_sea_correcto_en_el_caso_positivo(test_client):
    resultado = {"message": "La contraseña fue modificada correctamente."}
    app.dependency_overrides[get_recuperar_contraseña_use_case] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        resultado=resultado
        )
    app.dependency_overrides[get_token_service] = crear_override(
        stub_class=StubRecuperarContraseñaUseCase,
        resultado={"reset_token": "un_token_valido"}
    )

    test_client.cookies.set("reset_token", "un_token_valido")
    response = test_client.patch(
        f"/{settings.NOMBRE_APP}/usuarios/modificar/password",
        json={            
            "password": "Boca1234@"} #contraseña nueva
    )

    data = response.json()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert data["message"] == 'La contraseña fue modificada correctamente.'