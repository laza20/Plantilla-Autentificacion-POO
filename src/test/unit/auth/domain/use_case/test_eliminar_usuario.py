from src.test.fixtures.fixture_eliminar_usuario import EliminarUsuarioTestEnvironment
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.auth.domain.exceptions.usuarios_exceptions import LoginError, UsuarioNoEncontrado
import pytest
from src.test.factories.factory_sesiones import crear_sesion_de_prueba


def test_debe_logear_un_usuario_valido():
    """
    Verifica que un usuario pueda iniciar sesión correctamente con datos válidos.
    """
    context = EliminarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    crear_sesion_de_prueba(context.sesion_repository)

    resultado = context.use_case().ejecutar(token_hash=f"eliminacion_token_{usuario_creado.id_usuario}")

    assert resultado["message"] == "Usuario eliminado correctamente"