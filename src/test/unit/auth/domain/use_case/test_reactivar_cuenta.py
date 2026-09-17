import pytest
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.test.fixtures.fixture_reactivar_cuenta import ReactivarCuentaTestEnvironment
from src.auth.domain.exceptions.usuarios_exceptions import (
    UsuarioNoEncontrado, UsuarioNoEliminado, PeriodoReactivacionFinalizado
    )
from src.auth.domain.exceptions.tokens import TokenInvalido
from src.auth.domain.exceptions.domain import ErrorCreacion
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_verifica_que_se_reactiva_una_cuenta():
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    resultado = context.use_case().ejecutar(token=f"reactivacion_token_{usuario_creado.id_usuario}")
    assert resultado["message"] == "La cuenta fue reactivada correctamente."

@pytest.mark.parametrize(
    "token",
    [
        "",
        "hola",
        "reactivacion",
        "reactivacion_token",
        "access_token_1",
        "token_hola_1",
        "hola_token_1",
        "_reactivacion_token_1",
        "reactivacion_token_",
    ],
)
@pytest.mark.asyncio
async def test_debe_dar_error_por_token_invalido(token):
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    with pytest.raises(TokenInvalido):
        context.use_case().ejecutar(
            token=token
        )


@pytest.mark.asyncio
async def test_debe_dar_error_por_usuario_no_encontrado():
    context = ReactivarCuentaTestEnvironment()
    with pytest.raises(UsuarioNoEncontrado):
        context.use_case().ejecutar(
            token=f"reactivacion_token_55555"
        )


@pytest.mark.asyncio
async def test_debe_verificar_que_se_llamo_al_token_service():
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    resultado = context.use_case().ejecutar(token=f"reactivacion_token_{usuario_creado.id_usuario}")
    assert context.token_service.fue_llamado == True


@pytest.mark.asyncio
async def test_debe_verificar_al_ser_un_tiempo_posterior_al_posible_da_un_error_de_periodo_de_inactividad():
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.tiempo_eliminado = date.today() - timedelta(days=60)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    with pytest.raises(PeriodoReactivacionFinalizado):
        context.use_case().ejecutar(
            token=f"reactivacion_token_{usuario_creado.id_usuario}"
        )


@pytest.mark.asyncio
async def test_debe_verificar_que_se_produce_un_error_de_creacion():
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.accion_realizada = False
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    with pytest.raises(ErrorCreacion):
        context.use_case().ejecutar(
            token=f"reactivacion_token_{usuario_creado.id_usuario}"
        )