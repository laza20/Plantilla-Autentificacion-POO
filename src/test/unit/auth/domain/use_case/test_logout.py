from src.test.fixtures.fixture_logout_case import LogoutTestEnvironment
from test.factories.factory_sesiones import crear_sesion_de_prueba


def test_debe_verificar_que_se_elimino_el_token_en_el_repositorio():
    context = LogoutTestEnvironment()
    crear_sesion_de_prueba(context.token_repository, hash_token="hashed_token_de_prueba", user_agent="test")

    refresh_token = "token_de_prueba"
    refresh_token_hash = context.token_service.hash_token(refresh_token)
    context.use_case().ejecutar(refresh_token)
    assert context.token_repository.token_eliminado == refresh_token_hash