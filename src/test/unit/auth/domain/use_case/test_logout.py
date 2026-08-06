from fastapi import Response
from src.test.fixtures.fixture_logout_case import LogoutTestEnvironment


def test_debe_llamar_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    refresh_token = "token_de_prueba"
    use_case.logout(refresh_token, response)

    assert context.cookies_service.fue_llamado


def test_debe_enviar_el_response_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    refresh_token = "token_de_prueba"
    use_case.logout(refresh_token, response)

    assert context.cookies_service.response is response


def test_debe_verificar_que_se_elimino_el_token_en_el_repositorio():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    context.token_repository.insertar_sesion(
        hash_token="hashed_token_de_prueba",
        id_usuario=1,
        ip="127.0.0.1",
        user_agent="test"
    )
    refresh_token = "token_de_prueba"
    use_case.logout(refresh_token, response)
    assert context.token_repository.token_eliminado == context.token_service.hash_token(refresh_token)