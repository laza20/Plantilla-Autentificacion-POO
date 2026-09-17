from src.test.fixtures.fixture_eliminar_usuario import EliminarUsuarioTestEnvironment
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.auth.domain.exceptions.domain import ErrorEliminacion
import pytest
from src.test.factories.factory_sesiones import crear_sesion_de_prueba


def test_verifica_que_el_retorno_correcto_del_caso_de_uso():
    """
    Verifica que un usuario pueda iniciar sesión correctamente con datos válidos.
    """
    context = EliminarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    crear_sesion_de_prueba(context.sesion_repository)

    resultado = context.use_case().ejecutar(token_hash=f"eliminacion_token_{usuario_creado.id_usuario}")

    assert resultado["message"] == "Usuario eliminado correctamente"

def test_debe_verificar_que_se_eliminan_las_sesiones_de_un_usuario():
    context = EliminarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    crear_sesion_de_prueba(context.sesion_repository)

    resultado = context.use_case().ejecutar(token_hash=f"eliminacion_token_{usuario_creado.id_usuario}")

    assert context.sesion_repository.fue_llamado == True
    assert context.sesion_repository.sesiones_eliminadas > 0


def test_verifica_que_se_llamo_a_token_service():
    context = EliminarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    crear_sesion_de_prueba(context.sesion_repository)

    resultado = context.use_case().ejecutar(token_hash=f"eliminacion_token_{usuario_creado.id_usuario}")

    assert context.token_service.fue_llamado == True
