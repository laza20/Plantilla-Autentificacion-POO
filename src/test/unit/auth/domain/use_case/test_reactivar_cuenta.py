import pytest
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.test.fixtures.fixture_reactivar_cuenta import ReactivarCuentaTestEnvironment
from src.auth.domain.exceptions.usuarios_exceptions import (
    UsuarioNoEncontrado, UsuarioNoEliminado, PeriodoReactivacionFinalizado
    )
from src.auth.domain.exceptions.domain import ErrorCreacion
from src.test.factories.factory_usuarios import crear_usuario_de_prueba


@pytest.mark.asyncio
async def test_verifica_que_se_reactiva_una_cuenta():
    context = ReactivarCuentaTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    context.auth_user_repository.eliminar_usuario(usuario_creado)

    resultado = context.use_case().ejecutar(token=f"reactivacion_token_{usuario_creado.id_usuario}")
    assert resultado["message"] == "La cuenta fue reactivada correctamente."
