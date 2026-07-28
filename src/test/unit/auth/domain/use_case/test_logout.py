from fastapi import Response
from src.test.fixtures.fixture_logout_case import LogoutTestEnvironment


def test_debe_llamar_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    use_case.logout(response)

    assert context.cookies_service.fue_llamado


def test_debe_enviar_el_response_al_servicio_de_cookies():
    context = LogoutTestEnvironment()
    use_case = context.use_case()
    response = Response()
    use_case.logout(response)

    assert context.cookies_service.response is response