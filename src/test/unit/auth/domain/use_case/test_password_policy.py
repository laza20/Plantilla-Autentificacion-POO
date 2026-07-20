import pytest
from src.auth.domain.exceptions.domain import ContraseñaNoSegura
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO
from src.test.fixtures.fixture_register_case import RegisterTestEnvironment


@pytest.mark.asyncio
async def test_no_debe_registrar_un_usuario_con_password_sin_numeros():
    """
    Verifica que el registro rechaza usuarios cuya contraseña no cumple la política de seguridad por falta de numeros.
    """
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email="test@test.com",
        password="Password@asasa"
    )

    with pytest.raises(ContraseñaNoSegura):
        await context.use_case().register(usuario, imagen=None)