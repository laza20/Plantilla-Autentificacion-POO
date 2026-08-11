from src.test.fixtures.fixture_eliminar_sesiones import EliminarSesionesEnvironment


def test_eliminar_sesion_correctamente():
    """
    El test debe verificar que el caso de uso EliminarSesionesUseCase llama correctamente al método 
    eliminar_sesion del repositorio de sesiones.
    """
    context = EliminarSesionesEnvironment()
    id_usuario = 1
    hash_token = "hash_token_1"

    sesion_insertada = context.token_repository.insertar_sesion(
        hash_token=hash_token,
        id_usuario=id_usuario,
        ip="127.0.0.1",
        user_agent="user_agent_1")


    context.use_case().ejecutar(id_sesion=sesion_insertada.id_sesion, id_usuario=sesion_insertada.id_usuario)

    assert context.token_repository.fue_llamado is True
    assert context.token_repository.token_eliminado == sesion_insertada.hash_refresh_token
