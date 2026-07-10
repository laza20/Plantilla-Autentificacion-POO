import pytest
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO
from src.test.fixtures.fixture_register_case import RegisterTestEnvironment


@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_valido():
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email = "test@test.com",
        password = "Password123!"
    )
    usuario_creado = await context.use_case().register(
        usuario,
        imagen=None
    )

    assert usuario_creado.id_usuario is not None
    assert usuario_creado.password == "hashed_Password123!"
    assert len(context.user_repository._users) == 1


@pytest.mark.asyncio
async def test_no_debe_registrar_un_email_duplicado():
    context = RegisterTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password"
    )

    context.user_repository.insertar(usuario_existente)

    usuario = UserRegisterDTO(
        email="test@test.com",
        password="Password123!"
    )

    with pytest.raises(MailRepetido):
        await context.use_case().register(
            usuario,
            imagen=None
        )
