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


def test_se_encarga_de_verificar_que_la_contraseña_se_modifica():
    context = RecuperarContraseñaTestEnvironment()
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")
    contraseña_inicial = usuario_insertado.password

    context.auth_user_repository.modificar_contraseña(
        id_usuario=usuario_insertado.id_usuario,
        contraseña_nueva="nueva_contraseña",
        fecha_actual=datetime.now(timezone.utc)
    )

    usuario = context.auth_user_repository.obtener_por_email(email= usuario_insertado.email)
    assert contraseña_inicial != usuario.password


def test_debe_dar_error_por_que_no_se_pudo_desactivar_el_token():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    context.recuperar_contraseña_repository.desactivar_token_utilizado = lambda id_usuario: False

    with pytest.raises(TokenNoDesactivado):
        context.use_case().ejecutar(
            id_usuario=usuario_insertado.id_usuario,
            nueva_contraseña="nueva_contraseña"
        )