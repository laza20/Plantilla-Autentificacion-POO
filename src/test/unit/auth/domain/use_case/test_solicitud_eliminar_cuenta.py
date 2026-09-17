import pytest
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import UserRegisterDTO
from src.test.fixtures.fixture_solicitud_eliminar_usuario import SolicitudEliminacionUsuarioTestEnvironment
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.test.factories.factory_usuarios import crear_usuario_de_prueba


@pytest.mark.asyncio
async def test_verifica_que_se_solicita_una_eliminacion_de_cuenta_correctamente():
    context = SolicitudEliminacionUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)

    resultado = await context.use_case().ejecutar(usuario_creado.id_usuario)
    assert resultado["message"] == "Correo de eliminacion enviado a su mail."

@pytest.mark.asyncio
async def test_debe_verificar_que_se_produce_un_error_al_no_encontrar_al_usuario():
    context = SolicitudEliminacionUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository) #id usuario 1

    with pytest.raises(UsuarioNoEncontrado):
        await context.use_case().ejecutar(id_usuario=66)


@pytest.mark.asyncio
async def test_debe_verificar_que_se_llama_a_token_service():
    context = SolicitudEliminacionUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(usuario_creado.id_usuario)
    assert context.token_service.fue_llamado == True
    assert context.token_service.eliminacion_token_generado == f"eliminacion_token_{usuario_creado.id_usuario}"


@pytest.mark.asyncio
async def test_debe_verificar_que_se_llama_a_mail_service():
    context = SolicitudEliminacionUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(usuario_creado.id_usuario)
    assert context.mail_service.fue_llamado == True