from src.auth.domain.exceptions.tokens import TokenExpirado, TokenInvalido, VerificacionInvalida, VerificacionExpirada
import pytest
from src.test.fixtures.fixture_verify_mail_case import VerifyEmailTestEnvironment
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from fastapi import Response
from src.database.enums.estado_entidad import EstadoEntidad


def test_debe_verificar_el_mail_y_activar_el_usuario():
    """
    Verifica que un usuario pueda activar su cuenta mediante un token válido.

    El caso de uso debe:
    - verificar que el usuario exista.
    - validar el token recibido.
    - marcar al usuario como verificado y activo.
    """
    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.repository.insertar(usuario_existente)
    context.use_case().verificar_mail(
        token=f"access_token_{usuario.id_usuario}",
        response=Response()
    )
    usuario_activado = context.repository.obtener_por_email("test@test.com")

    assert usuario_activado.estado == EstadoEntidad.ACTIVO
    assert usuario_activado.is_verified is True
    assert context.token_service.user_id_recibido == usuario.id_usuario


def test_debe_verificar_que_los_tokens_sean_adecuados():
    """
    Verifica que los tokens recibidos sean adeacuados en referencia a los tokens generados.
    """
    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.repository.insertar(usuario_existente)
    tokens = context.use_case().verificar_mail(token= f"access_token_{usuario.id_usuario}", response= Response())

    assert tokens.access_token == context.token_service.access_token_generado
    assert tokens.refresh_token == context.token_service.refresh_token_generado


def test_debe_verificar_que_se_llama_al_servicio_de_cookies():
    """
    El test se debe encargar de verificar que en el flujo de la activacion de la cuenta por medio
    del mail enviado, las cookies se setean correctamente, en este caso el stub, que solo realiza
    modificaciones de los parametros.
    """

    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.repository.insertar(usuario_existente)
    context.use_case().verificar_mail(
        token=f"access_token_{usuario.id_usuario}",
        response=Response()
    )

    assert context.cookies_service.fue_llamado is True
    assert context.cookies_service.access_token == f"access_token_{usuario.id_usuario}"
    assert context.cookies_service.refresh_token is not None