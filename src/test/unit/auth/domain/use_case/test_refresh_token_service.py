import pytest
from src.test.fixtures.fixture_refresh_token_case import RefreshTokenTestEnvironment
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.test.unit.auth.domain.fakes.fake_user_repository import FakeUserRepository
from fastapi import Response

def test_debe_verificar_el_flujo_correcto_del_refresh():
    context_refresh = RefreshTokenTestEnvironment()
    context_repository = FakeUserRepository()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context_repository.insertar(usuario_existente)

    context_refresh.use_case().refreshed_token(refresh_token=f"refresh_token_{usuario.id_usuario}",
            response=Response())
        
    assert context_refresh.token_service.user_id_recibido == usuario.id_usuario
    assert context_refresh.cookies_service.fue_llamado is True
    assert context_refresh.cookies_service.access_token == context_refresh.token_service.access_token_generado