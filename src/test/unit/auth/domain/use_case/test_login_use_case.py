from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.test.fixtures.fixture_login_case import LoginTestEnvironment
from fastapi import Response
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioError, LoginError, UsuarioNoEncontrado
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO
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
    
    assert cookies.tokens.access_token == "access_token_1"
    assert cookies.tokens.refresh_token == "refresh_token_1"
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