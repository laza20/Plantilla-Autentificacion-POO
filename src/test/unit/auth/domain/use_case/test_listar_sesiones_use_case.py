from src.test.fixtures.fixture_listar_sesiones import ListarSesionesEnvironment


def test_listar_sesiones_usuario_logeado_correctamente():
    """
    Verifica que se puedan listar las sesiones de un usuario correctamente.
    """
    contex_listar_sesion = ListarSesionesEnvironment()

    contex_listar_sesion.token_repository.insertar_sesion(
        hash_token="sample_hash_token",
        id_usuario=1,
        ip="127.0.0.1",
        user_agent="sample_user_agent"
    )

    sesiones = contex_listar_sesion.use_case().ejecutar(id_usuario=1, ip="127.0.0.1")
    assert len(sesiones.sesiones) == 1
    assert sesiones.sesiones[0].id_usuario == 1
    assert sesiones.sesiones[0].ip == "127.0.0.1"
    assert sesiones.sesiones[0].user_agent == "sample_user_agent"
