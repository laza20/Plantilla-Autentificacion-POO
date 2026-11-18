from dataclasses import asdict
from src.auth.application.mappers.auth_users import a_usuario_creado
from src.auth.domain.entities.entitie_auth_users import AuthUser


def test_a_usuario_creado_copia_los_campos_publicos():
    entidad = AuthUser(email="a@b.com", password="secreta", id_usuario=1, is_verified=True)

    dto = a_usuario_creado(entidad)

    assert (dto.id_usuario, dto.email, dto.is_verified) == (1, "a@b.com", True)


def test_a_usuario_creado_no_expone_password():
    entidad = AuthUser(email="a@b.com", password="secreta", id_usuario=1)

    assert "password" not in asdict(a_usuario_creado(entidad))