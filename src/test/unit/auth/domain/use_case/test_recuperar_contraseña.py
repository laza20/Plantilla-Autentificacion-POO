from src.test.fixtures.fixture_recuperar_contraseña import RecuperarContraseñaTestEnvironment
from src.test.factories.factory_create_password_recover import crear_recover_password_de_prueba
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.auth.domain.exceptions.tokens import TokenNoDesactivado
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoModificado, UsuarioNoEncontrado
from src.auth.domain.exceptions.domain import ErrorCreacion
import pytest
from datetime import datetime, timezone


def test_debe_verificar_el_retorno_al_suceder_el_camino_optimo():
    """
    El test se encarga de verificar que en el caso de que todo funcione correctamente se realicen de manera
    correcta.
    """
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    resultado = context.use_case().ejecutar(
        id_usuario=usuario_insertado.id_usuario,
        nueva_contraseña="nueva_contraseña"
    )

    assert resultado["message"] == "La contraseña fue modificada correctamente."