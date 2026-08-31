from src.test.fixtures.fixture_solicitud_recuperacion_contraseña import SolicitudRecuperacionContraseñaTestEnvironment
import pytest
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioError

@pytest.mark.asyncio
async def test_debe_realizar_la_solicitud_de_recuperacion_de_manera_correcta():
    """
    Realiza la peticion para reestablecer una contraseña de manera correcta.
    """
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    resultado = await context.use_case().ejecutar(
        usuario.email
    )

    assert resultado["message"] == "Mail enviado correctamente, revise su bandeja de entrada, si no lo encuentra revise en spam o correos no deseados."


@pytest.mark.asyncio
async def test_debe_verificar_que_mail_service_fue_llamado_correctamente():
    """
    El test se encarga de verificar que en el caso de que todo funcione correctamente se realicen de manera
    correcta las llamadas al servicio de mail.
    """
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(
        usuario.email
    )

    assert context.mail_service.fue_llamado == True


@pytest.mark.asyncio
async def test_debe_verificar_que_token_service_fue_llamado_y_funciona_correctamente():
    """
    El test se encarga de verificar que en el caso de que todo funcione correctamente se realicen de manera
    correcta las llamadas al servicio de token.
    """
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(
        usuario.email
    )

    assert context.token_service.fue_llamado == True
    assert context.token_service.hash_token == "hashed_1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"


@pytest.mark.asyncio
async def test_debe_verificar_que_se_llamo_de_manera_correcta_a_unit_od_work_para_verificar_el_funcionamiento():
    """
    El test se encarga de verificar que la unidad de trabajo, la cual es la encargada de chequear
    el funcionamiento con la base de datos se llamo correctamente.
    """

    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(
        usuario.email
    )

    assert context.unit_of_work_service.fue_llamado == True

@pytest.mark.asyncio
async def test_debe_verificar_que_se_llamo_de_manera_correcta_al_repositorio_de_recuperacion_de_contraseña():
    """
    El test se encarga de verificar que el repositorio el cual corresponde a la insercion de una
    recuperacion de contraseña fue utilizado correctamente
    """

    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    await context.use_case().ejecutar(
        usuario.email
    )

    assert context.recuperar_contraseña_repository.fue_llamado == True
    assert context.recuperar_contraseña_repository.token_hash == "hashed_1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7"
    assert len(context.recuperar_contraseña_repository.tokens) != 0


@pytest.mark.asyncio
async def test_debe_verificar_que_se_produce_un_error_si_no_se_encuentra_el_usuario():
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    with pytest.raises(UsuarioError):
        await context.use_case().ejecutar(
            "usuario.email@"
        )
