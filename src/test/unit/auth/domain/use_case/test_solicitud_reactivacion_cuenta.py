import pytest
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import UserRegisterDTO
from src.test.fixtures.fixture_solicitud_reactivacion_cuenta import SolicitudReactivacionCuentaTestEnvironment
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.test.factories.factory_usuarios import crear_usuario_de_prueba


@pytest.mark.asyncio
async def test_verifica_que_se_solicita_una_reactivacion_de_cuenta_correctamente():
    context = SolicitudReactivacionCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    resultado = await context.use_case().ejecutar(usuario_creado.email)
    assert resultado["message"] == "Correo enviado correctamente"

@pytest.mark.asyncio
async def test_verifica_que_se_llamo_al_mail_service():
    context = SolicitudReactivacionCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    await context.use_case().ejecutar(usuario_creado.email)
    assert context.mail_service.fue_llamado != False


@pytest.mark.asyncio
async def test_verifica_que_se_llamo_al_token_service():
    context = SolicitudReactivacionCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    await context.use_case().ejecutar(usuario_creado.email)
    assert context.token_service.fue_llamado != False


@pytest.mark.asyncio
async def test_verifica_que_se_llamo_al_token_service():
    context = SolicitudReactivacionCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    await context.use_case().ejecutar(usuario_creado.email)
    assert context.token_service.fue_llamado != False
    assert context.token_service.reactivacion_token_generado == f"reactivacion_token_{usuario_creado.id_usuario}"
