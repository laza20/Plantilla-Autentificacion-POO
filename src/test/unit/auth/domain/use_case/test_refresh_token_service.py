import pytest
from src.test.fixtures.fixture_refresh_token_case import RefreshTokenTestEnvironment
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from fastapi import Response
from src.auth.domain.exceptions.tokens import VerificacionInvalida

def test_debe_verificar_el_flujo_correcto_del_refresh():
    context_refresh = RefreshTokenTestEnvironment()
    context_repository = FakeUserRepository()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context_repository.insertar(usuario_existente)

    context_refresh.use_case().refreshed_token(refresh_token=f"refresh_token_{usuario.id_usuario}",
            response=Response())
        
    assert context_refresh.token_service.user_id_recibido == usuario.id_usuario
    assert context_refresh.cookies_service.fue_llamado is True
    assert context_refresh.cookies_service.access_token == context_refresh.token_service.access_token_generado

@pytest.mark.parametrize(
    "token",
    [
        "",
        "hola",
        "refresh",
        "refresh_token",
        "access_token_1",
        "token_hola_1",
        "hola_token_1",
        "_refresh_token_1",
        "refresh_token_",
    ],
)
def test_debe_dar_error_cuando_el_formato_del_token_es_invalido(token):
    """
    Verifica que cualquier token con un formato inválido produzca
    una excepción VerificacionInvalida.
    """
    context = RefreshTokenTestEnvironment()

    with pytest.raises(VerificacionInvalida):
        context.use_case().refreshed_token(
            refresh_token=token,
            response=Response(),
        )


def test_debe_verificar_que_el_response_sea_correcto():
    """
    Verifica que el response tenga el access token correcto después de refrescar.
    """
    context_refresh = RefreshTokenTestEnvironment()
    response = Response()
    context_refresh.use_case().refreshed_token(refresh_token=f"refresh_token_1",
            response=response)

    assert context_refresh.cookies_service.response is response


def test_debe_verificar_que_el_servicio_de_token_fue_llamado_con_el_id_correcto():
    """
    Verifica que el servicio de token haya sido llamado con el ID de usuario correcto.
    """
    context_refresh = RefreshTokenTestEnvironment()
    user_id = 42
    context_refresh.use_case().refreshed_token(refresh_token=f"refresh_token_{user_id}",
            response=Response())

    assert context_refresh.token_service.user_id_recibido == user_id