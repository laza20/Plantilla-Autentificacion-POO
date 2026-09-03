from src.test.fixtures.fixture_listar_sesiones import ListarSesionesEnvironment
from src.test.factories.factory_sesiones import crear_sesion_de_prueba


def test_listar_sesiones_usuario_logeado_correctamente():
    """
    Verifica que se puedan listar las sesiones de un usuario correctamente.
    """
    contex_listar_sesion = ListarSesionesEnvironment()

    crear_sesion_de_prueba(contex_listar_sesion.sesion_repository)

    sesiones = contex_listar_sesion.use_case().ejecutar(id_usuario=1, ip="127.0.0.1")
    assert len(sesiones.sesiones) == 1
    assert sesiones.sesiones[0].id_usuario == 1
    assert sesiones.sesiones[0].ip == "127.0.0.1"
    assert sesiones.sesiones[0].user_agent == "user_agent_1"


def test_listar_sesiones_usuario_sin_sesiones():
    """
    Verifica que se devuelva una lista vacía si el usuario no tiene sesiones activas.
    """
    contex_listar_sesion = ListarSesionesEnvironment()

    sesiones = contex_listar_sesion.use_case().ejecutar(id_usuario=2, ip="127.0.0.1")

    assert len(sesiones.sesiones) == 0

def test_debe_listar_varias_sesiones_y_marcar_la_actual():
    """
    Verifica que se puedan listar varias sesiones de un usuario y marcar la sesión actual.
    """
    contex_listar_sesion = ListarSesionesEnvironment()

    crear_sesion_de_prueba(contex_listar_sesion.sesion_repository)
    crear_sesion_de_prueba(
        contex_listar_sesion.sesion_repository,  
        hash_token="hash_token_2", 
        ip= "128.0.0.1", 
        user_agent="user_agent_2"
        )

    sesiones = contex_listar_sesion.use_case().ejecutar(id_usuario=1, ip="127.0.0.1")

    assert len(sesiones.sesiones) == 2
    assert sesiones.sesiones[0].es_actual is True
    assert sesiones.sesiones[1].es_actual is False


def test_debe_listar_varias_sesiones_sin_la_ip_actual():
    """
    Verifica que se puedan listar varias sesiones de un usuario sin una sesion marcada como actual si la IP no coincide con ninguna sesión.
    """
    contex_listar_sesion = ListarSesionesEnvironment()

    crear_sesion_de_prueba(contex_listar_sesion.sesion_repository)
    crear_sesion_de_prueba(
        contex_listar_sesion.sesion_repository,  
        hash_token="hash_token_2", 
        ip= "128.0.0.1", 
        user_agent="user_agent_2"
        )

    sesiones = contex_listar_sesion.use_case().ejecutar(id_usuario=1, ip="129.0.0.1")

    assert sesiones.sesiones[0].es_actual is False
    assert sesiones.sesiones[1].es_actual is False