from fastapi import Response
from src.test.fixtures.fixture_logout_case import LogoutTestEnvironment
from test.factories.factory_sesiones import crear_sesion_de_prueba


def test_debe_llamar_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    refresh_token = "token_de_prueba"
    use_case.ejecutar(refresh_token, response)

    assert context.cookies_service.fue_llamado


def test_debe_enviar_el_response_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    refresh_token = "token_de_prueba"
    use_case.ejecutar(refresh_token, response)

    assert context.cookies_service.response is response


def test_debe_verificar_que_se_elimino_el_token_en_el_repositorio():
    context = LogoutTestEnvironment()
    response = Response()
    crear_sesion_de_prueba(context.token_repository, hash_token="hashed_token_de_prueba", user_agent="test")

    refresh_token = "token_de_prueba"
    context.use_case().ejecutar(refresh_token, response)
    assert context.token_repository.token_eliminado == context.token_service.hash_token(refresh_token)