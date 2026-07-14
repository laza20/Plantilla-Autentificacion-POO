import pytest
from src.auth.infrastructure.persistence.postgres.models import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.auth.domain.exceptions.domain import ContraseñaNoSegura
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO
from src.test.fixtures.fixture_register_case import RegisterTestEnvironment
from io import BytesIO
from fastapi import UploadFile


@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_valido():
    """
    Verifica que un usuario sea registrado correctamente con datos válidos.
    """
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
    """
    Verifica que un usuario al ser registrado con un mail ya existente produzca un error 
    y no pueda registrarse
    """
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

@pytest.mark.asyncio
async def test_no_debe_registrar_un_usuario_con_password_invalida():
    """
    Verifica que el registro rechaza usuarios cuya contraseña no cumple la política de seguridad.
    """
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email="test@test.com",
        password="Password"
    )

    with pytest.raises(ContraseñaNoSegura):
        await context.use_case().register(usuario, imagen=None)

@pytest.mark.asyncio
async def test_no_debe_registrar_un_usuario_sin_datos():
    """
    Verifica que un usuario registrado sea rechazado al ser none.
    """
    context = RegisterTestEnvironment()

    with pytest.raises(SinCargas):
        await context.use_case().register(None, imagen=None)


@pytest.mark.asyncio
async def test_registro_verifica_normalizacion_de_datos():
    """
    verifica que la normalizacion funciona correctamente.
    """
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email="   TEST@TEST.COM",
        password="Password123!"
    )

    usuario_creado = await context.use_case().register(
        usuario,
        imagen=None
        )
    
    assert usuario_creado.email == "test@test.com"


@pytest.mark.asyncio
async def test_debe_lanzar_error_si_el_email_supera_la_longitud_maxima():
    """
    Verifica que un usuario registrado con mayor tamaño del esperado produzca un error de longitud excedida.
    """
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email="" + "a" * 250 + "@test.com",
        password="Password123!"
    )


    with pytest.raises(LongitudExcedida):
        await context.use_case().register(usuario, imagen=None)

@pytest.mark.asyncio
async def test_registro_con_imagen():
    """
    Verifica que un usuario sea registrado correctamente con datos válidos y una imagen.
    """
    context = RegisterTestEnvironment()

    usuario = UserRegisterDTO(
        email = "test@test.com",
        password = "Password123!"
    )
    imagen = UploadFile(
        filename="foto.jpg",
        file=BytesIO(b"contenido")
    )
    usuario_creado = await context.use_case().register(
        usuario,
        imagen=imagen
    )

    assert usuario_creado.imagen_url == "usuarios_imagen_ficticia.jpg"