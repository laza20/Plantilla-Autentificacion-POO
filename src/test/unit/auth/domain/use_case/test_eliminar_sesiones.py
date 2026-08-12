from src.test.fixtures.fixture_eliminar_sesiones import EliminarSesionesEnvironment
from test.factories.factory_sesiones import crear_sesion_de_prueba

def test_eliminar_sesion_correctamente():
    """
    El test debe verificar que el caso de uso EliminarSesionesUseCase llama correctamente al método 
    eliminar_sesion del repositorio de sesiones.
    """
    context = EliminarSesionesEnvironment()
    sesion_insertada = crear_sesion_de_prueba(context.token_repository)

    context.use_case().ejecutar(id_sesion=sesion_insertada.id_sesion, id_usuario=sesion_insertada.id_usuario)

    assert context.token_repository.fue_llamado is True
    assert context.token_repository.token_eliminado == sesion_insertada.hash_refresh_token

def test_eliminar_sesion_que_no_existe():
    """
    El test debe verificar que el usuario quiere eliminar una sesion que no existe.
    """
    context = EliminarSesionesEnvironment()
    sesion_insertada = crear_sesion_de_prueba(context.token_repository)


    context.use_case().ejecutar(id_sesion=5, id_usuario=sesion_insertada.id_usuario)

    assert context.token_repository.fue_llamado is True
    assert context.token_repository.token_eliminado == None



def test_debe_verificar_que_la_sesion_fue_eliminada_correctamente_y_el_retorno_es_correcto():
    """
    El test se encarga de verificar que a la sucesion de pasos llega a la conclusion correcta y 
    el retorno es el esperado para el caso positivo.
    """
    context = EliminarSesionesEnvironment()
    sesion_insertada = crear_sesion_de_prueba(context.token_repository)


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
    sesion_insertada = crear_sesion_de_prueba(context.token_repository)


    resultado = context.use_case().ejecutar(
        id_sesion=50, 
        id_usuario=sesion_insertada.id_usuario
        )

    assert resultado["message"] == "La sesion que se quiso eliminar, no pudo ser encontrada"