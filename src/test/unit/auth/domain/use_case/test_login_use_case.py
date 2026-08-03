from auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.test.fixtures.fixture_login_case import LoginTestEnvironment
from fastapi import Response
from src.auth.domain.exceptions.usuarios_exceptions import LoginError, UsuarioNoEncontrado
import pytest


def test_debe_logear_un_usuario_valido():
    """
    Verifica que un usuario pueda iniciar sesión correctamente con datos válidos.
    """
    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    context.user_repository.insertar(usuario_existente)


    cookies = context.use_case().login(
        email="test@test.com",
        password="password@123",
        response=Response()
    )
    
    assert cookies.tokens.access_token == context.token_service.access_token_generado
    assert cookies.tokens.refresh_token == context.token_service.refresh_token_generado
    assert cookies.tokens.token_type == "bearer"


def test_debe_dar_error_cuando_el_usuario_no_existe():
    """
    Verifica que se devuelva un error cuando el usuario no existe.
    """
    context = LoginTestEnvironment()
    
    with pytest.raises(UsuarioNoEncontrado):
        context.use_case().login(        
            email = "test@test.com",
            password = "Password123!", 
            response=Response()
            )



def test_debe_dar_error_cuando_la_contrasena_es_incorrecta():
    """
    Verifica que se devuelva un error cuando la contraseña es incorrecta.
    """
    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    context.user_repository.insertar(usuario_existente)

    with pytest.raises(LoginError):
        context.use_case().login(
            email="test@test.com",
            password="wrong_password",
            response=Response()
        )


def test_verifica_que_tokens_es_llamado_correctamente():
    """
    Verifica que los tokens de acceso y actualización se emitan correctamente al iniciar sesión.
    """
    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    context.user_repository.insertar(usuario_existente)


    cookies = context.use_case().login(
        email="test@test.com",
        password="password@123",
        response=Response()
    )
    
    assert context.token_service.fue_llamado is True


def test_verifica_que_cookies_service_es_llamado_correctamente():
    """
    Verifica que el servicio de cookies se llame correctamente al iniciar sesión.
    """
    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    context.user_repository.insertar(usuario_existente)


    cookies = context.use_case().login(
        email="test@test.com",
        password="password@123",
        response=Response()
    )
    
    assert context.cookies_service.fue_llamado is True


def test_verifica_que_el_usuario_publico_se_retorna_correctamente():
    """
    Verifica que el usuario público se retorne correctamente al iniciar sesión.
    """
    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123",
        imagen_url="http://example.com/image.jpg"
    )

    context.user_repository.insertar(usuario_existente)

    cookies = context.use_case().login(
        email="test@test.com",
        password="password@123",
        response=Response()
    )

    assert cookies.usuario.email == "test@test.com"
    assert cookies.usuario.imagen_url == "http://example.com/image.jpg"




def test_debe_verificar_el_id_del_usuario():
    """
    Verifica que el ID del usuario se pase correctamente al servicio de tokens al iniciar sesión.
    """

    context = LoginTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123",
        imagen_url="http://example.com/image.jpg"
    )

    context.user_repository.insertar(usuario_existente)

    cookies = context.use_case().login(
        email="test@test.com",
        password="password@123",
        response=Response()
    )

    assert context.token_service.user_id_recibido == 1