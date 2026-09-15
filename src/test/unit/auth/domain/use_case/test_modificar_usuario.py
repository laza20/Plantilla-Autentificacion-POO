import pytest
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import (
    AuthUser, AuthUserEmailValidation, UserModifyDTO)
from src.test.fixtures.fixture_modificar_usuario import ModificarUsuarioUseCase
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import UserModifyDTO
from io import BytesIO
from fastapi import UploadFile
from src.auth.domain.exceptions.domain import LongitudExcedida
from src.database.enums.estado_entidad import EstadoEntidad
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioNoModificado
from src.test.fixtures.fixture_modificar_usuario import ModificarUsuarioTestEnvironment
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from pydantic import ValidationError



@pytest.mark.asyncio
async def test_debe_verificar_que_se_modifica_el_usuario():
    context = ModificarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    modificacion = UserModifyDTO(
        email = "test@test_nuevo.com"
    )
    usuario_modificado = await context.use_case().ejecutar(
        id_usuario=usuario_creado.id_usuario, usuario=modificacion, imagen= None
        )

    assert usuario_creado != usuario_modificado

@pytest.mark.asyncio
async def test_debe_modificar_un_mail_correctamente():
    context = ModificarUsuarioTestEnvironment()
    usuario_creado = crear_usuario_de_prueba(context.auth_user_repository)
    modificacion = UserModifyDTO(
        email = "test@test_nuevo.com"
    )
    usuario_modificado = await context.use_case().ejecutar(
        id_usuario=usuario_creado.id_usuario, usuario=modificacion, imagen= None
        )

    assert usuario_creado.email != usuario_modificado.email
