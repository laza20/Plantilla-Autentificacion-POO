import pytest
from src.test.fixtures.fixture_refresh_token_case import RefreshTokenTestEnvironment
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.auth.domain.exceptions.tokens import VerificacionInvalida


def test_debe_verificar_el_flujo_correcto_del_refresh():
    context_refresh = RefreshTokenTestEnvironment()
    context_repository = FakeUserRepository()

    usuario = crear_usuario_de_prueba(context_repository)

    context_refresh.use_case().ejecutar(refresh_token=f"refresh_token_{usuario.id_usuario}")
        
    assert context_refresh.token_service.user_id_recibido == usuario.id_usuario

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
        context.use_case().ejecutar(
            refresh_token=token
        )




def test_debe_verificar_que_el_servicio_de_token_fue_llamado_con_el_id_correcto():
    """
    Verifica que el servicio de token haya sido llamado con el ID de usuario correcto.
    """
    context_refresh = RefreshTokenTestEnvironment()
    user_id = 42
    context_refresh.use_case().ejecutar(refresh_token=f"refresh_token_{user_id}")

    assert context_refresh.token_service.user_id_recibido == user_id