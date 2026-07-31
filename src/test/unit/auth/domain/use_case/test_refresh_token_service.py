import pytest
from src.test.fixtures.fixture_refresh_token_case import RefreshTokenTestEnvironment
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.test.unit.auth.domain.fakes.fake_user_repository import FakeUserRepository

def test_debe_verificar_el_flujo_correcto_del_refresh():
    context_refresh = RefreshTokenTestEnvironment()
    context_repository = FakeUserRepository()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    context_repository.user_repository.insertar(usuario_existente)

    context_refresh.use_case.refreshed_token()