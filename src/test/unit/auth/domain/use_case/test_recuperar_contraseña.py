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


def test_debe_verificar_que_se_produce_un_error_cuando_el_usuario_no_existe():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)

    with pytest.raises(UsuarioNoEncontrado):
        context.use_case().ejecutar(
            id_usuario=9999,
            nueva_contraseña="nueva_contraseña"
        )


def test_debe_saltar_una_excepcion_al_producirse_un_error_a_la_hora_de_crear_un_history_password():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    context.history_contraseña_repository.insertar_history_repository = lambda id_usuario, password_hash_anterior, fecha_cambio: False

    with pytest.raises(ErrorCreacion):
        context.use_case().ejecutar(
            id_usuario=usuario_insertado.id_usuario,
            nueva_contraseña="nueva_contraseña"
        )


def test_debe_producirse_un_error_al_no_poder_modificarse_un_usuario():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    context.auth_user_repository.modificar_contraseña = lambda id_usuario, contraseña_nueva, fecha_actual: False

    with pytest.raises(UsuarioNoModificado):
        context.use_case().ejecutar(
            id_usuario=usuario_insertado.id_usuario,
            nueva_contraseña="nueva_contraseña"
        )


def test_debe_verificar_que_se_guarda_un_history_password_cuando_se_modifica_la_contraseña():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    context.use_case().ejecutar(
        id_usuario=usuario_insertado.id_usuario,
        nueva_contraseña="nueva_contraseña"
    )

    history_password_guardado = context.history_contraseña_repository.history_password.get(usuario_insertado.id_usuario)
    assert history_password_guardado is not None

def test_debe_verificar_que_se_hashea_la_contraseña_antes_de_guardarse():
    context = RecuperarContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    usuario_insertado = crear_usuario_de_prueba(context.auth_user_repository, password="contraseña_inicial")

    nueva_contraseña = "nueva_contraseña"
    context.use_case().ejecutar(
        id_usuario=usuario_insertado.id_usuario,
        nueva_contraseña=nueva_contraseña
    )

    usuario_actualizado = context.auth_user_repository.obtener_por_id(id_usuario=usuario_insertado.id_usuario)
    assert usuario_actualizado.password != nueva_contraseña