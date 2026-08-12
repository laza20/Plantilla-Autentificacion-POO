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

def test_eliminar_sesion_que_no_existe():
    """
    El test debe verificar que el usuario quiere eliminar una sesion que no existe.
    """
    context = EliminarSesionesEnvironment()
    id_usuario = 1
    hash_token = "hash_token_1"

    sesion_insertada = context.token_repository.insertar_sesion(
        hash_token=hash_token,
        id_usuario=id_usuario,
        ip="127.0.0.1",
        user_agent="user_agent_1")


    resultado = context.use_case().ejecutar(id_sesion=5, id_usuario=sesion_insertada.id_usuario)

    assert context.token_repository.fue_llamado is True
    assert context.token_repository.token_eliminado == None



def test_debe_verificar_que_la_sesion_fue_eliminada_correctamente_y_el_retorno_es_correcto():
    """
    El test se encarga de verificar que a la sucesion de pasos llega a la conclusion correcta y 
    el retorno es el esperado para el caso positivo.
    """
    context = EliminarSesionesEnvironment()
    id_usuario = 1
    hash_token = "hash_token_1"

    sesion_insertada = context.token_repository.insertar_sesion(
        hash_token=hash_token,
        id_usuario=id_usuario,
        ip="127.0.0.1",
        user_agent="user_agent_1")


    resultado = context.use_case().ejecutar(
        id_sesion=sesion_insertada.id_sesion, 
        id_usuario=sesion_insertada.id_usuario
        )

    assert resultado["message"] == "Sesión eliminada"


def test_debe_verificar_que_la_sesion_no_fue_eliminada_correctamente_y_el_retorno_es_adecuado():
    """
    El test se encarga de verificar que a la sucesion de pasos llega a la conclusion correcta y 
    el retorno es el esperado para el caso negativo.
    """
    context = EliminarSesionesEnvironment()
    id_usuario = 1
    hash_token = "hash_token_1"

    sesion_insertada = context.token_repository.insertar_sesion(
        hash_token=hash_token,
        id_usuario=id_usuario,
        ip="127.0.0.1",
        user_agent="user_agent_1")


    resultado = context.use_case().ejecutar(
        id_sesion=50, 
        id_usuario=sesion_insertada.id_usuario
        )

    assert resultado["message"] == "La sesion que se quiso eliminar, no pudo ser encontrada"