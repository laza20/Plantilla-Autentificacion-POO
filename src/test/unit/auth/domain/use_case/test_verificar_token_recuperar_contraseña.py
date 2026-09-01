from src.test.fixtures.fixture_verificar_token_recuperacion_contraseña import VerificarTokenRecuperacionContraseñaTestEnvironment
from src.test.factories.factory_create_password_recover import crear_recover_password_de_prueba
from src.auth.domain.exceptions.tokens import TokenNoVerificado
import pytest
from datetime import datetime, timezone


def test_debe_verificar_que_token_service_fue_llamado_y_funciona_correctamente():
    """
    El test se encarga de verificar que en el caso de que todo funcione correctamente se realicen de manera
    correcta las llamadas al servicio de token.
    """
    context = VerificarTokenRecuperacionContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    context.use_case().ejecutar(
        "1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"
    )

    assert context.token_service.fue_llamado == True
    assert context.token_service.hash_token == "hashed_1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"

def test_debe_verificar_que_al_pasarse_un_token_invalido_genera_un_error_de_tipo_TokenInvalido():
    """
    El test se encarga de verificar que en el caso de que se pase un token invalido, el caso de uso
    genera un error de tipo TokenInvalido.
    """
    context = VerificarTokenRecuperacionContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)

    with pytest.raises(TokenNoVerificado):
        context.use_case().ejecutar(
            "1a2s3w5e6g9s" #token invalido
        )

def test_debe_verificar_que_al_pasarse_un_token_expirado_genera_un_error_de_tipo_TokenInvalido():
    """
    El test se encarga de verificar que en el caso de que se pase un token expirado, el caso de uso
    genera un error de tipo TokenInvalido.
    """
    context = VerificarTokenRecuperacionContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(
        context.recuperar_contraseña_repository,
        fecha_expiracion=datetime(
            2023, 1, 1,
            tzinfo=timezone.utc
        ))

    with pytest.raises(TokenNoVerificado):
        context.use_case().ejecutar(
            "1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"
        )


def test_debe_verificar_que_al_pasarse_un_token_usado_genera_un_error_de_tipo_TokenInvalido():
    """
    El test se encarga de verificar que en el caso de que se pase un token usado, el caso de uso
    genera un error de tipo TokenInvalido.
    """
    context = VerificarTokenRecuperacionContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    context.recuperar_contraseña_repository.invalidar_tokens_anteriores(id_usuario=1)

    with pytest.raises(TokenNoVerificado):
        context.use_case().ejecutar(
            "1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"
        )


def test_debe_verificar_que_el_retorno_sea_un_token_de_tipo_reset():
    """
    El test se encarga de verificar que en el caso de que todo funcione correctamente, 
    el retorno del caso de uso sea un token de tipo reset
    """

    context = VerificarTokenRecuperacionContraseñaTestEnvironment()
    sesion_insertada = crear_recover_password_de_prueba(context.recuperar_contraseña_repository)
    token_retorno = context.use_case().ejecutar(
        "1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"
    )

    assert token_retorno == f"reset_token_1" #1 por el id_usuario (seria f"reset_token_{id_usuario}")