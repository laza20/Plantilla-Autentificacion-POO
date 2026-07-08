import pytest
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido
from src.auth.application.use_cases.register import RegisterUseCase
from src.test.unit.auth.domain.service import (
    stub_image_service,
    stub_mail_service,
    stub_password_service,
    stub_token_service
)
from src.test.unit.auth.domain.fakes.fake_user_repository import FakeUserRepository
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO
from src.auth.domain.services.password_policy import PasswordPolicyService
from src.test.config.config import TestSettings



@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_valido():

    repository = FakeUserRepository()
    password_service = stub_password_service.StubPasswordService()
    token_service = stub_token_service.StubTokenService()
    mail_service = stub_mail_service.StubMailService()
    image_service = stub_image_service.StubImageService()
    password_policy = PasswordPolicyService()
    settings = TestSettings()

    use_case = RegisterUseCase(
        repository,
        password_service,
        mail_service,
        image_service,
        token_service,
        password_policy,
        settings
    )

    usuario = UserRegisterDTO(
        email = "test@test.com",
        password = "Password123!"
    )

    # Act
    usuario_creado = await use_case.register(
        usuario,
        imagen=None
    )

    assert usuario_creado.id_usuario is not None
    assert usuario_creado.password == "hashed_Password123!"
    assert len(repository._users) == 1


@pytest.mark.asyncio
async def test_no_debe_registrar_un_email_duplicado():

    # ==========================
    # Arrange
    # ==========================

    repository = FakeUserRepository()
    password_service = stub_password_service.StubPasswordService()
    token_service = stub_token_service.StubTokenService()
    mail_service = stub_mail_service.StubMailService()
    image_service = stub_image_service.StubImageService()
    password_policy = PasswordPolicyService()
    settings = TestSettings()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password"
    )

    repository.insertar(usuario_existente)

    use_case = RegisterUseCase(
        repository,
        password_service,
        mail_service,
        image_service,
        token_service,
        password_policy,
        settings
    )

    usuario = UserRegisterDTO(
        email="test@test.com",
        password="Password123!"
    )


    with pytest.raises(MailRepetido):
        await use_case.register(
            usuario,
            imagen=None
        )
