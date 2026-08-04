import pytest
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from src.auth.domain.exceptions.domain import MailRepetido, SinCargas, LongitudExcedida
from src.auth.infrastructure.persistence.postgres.models_auth_users import UserRegisterDTO
from src.test.fixtures.fixture_register_case import RegisterTestEnvironment
from src.auth.domain.exceptions.domain import ContraseñaNoSegura, MailNoValido
from io import BytesIO
from fastapi import UploadFile


@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_valido_sin_imagen():
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

    assert context.image_service.fue_llamado is False


@pytest.mark.asyncio
async def test_debe_crear_un_usuario():
    """
    Verifica que un usuario sea creado correctamente con datos válidos.
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

@pytest.mark.asyncio
async def test_debe_hashear_la_contraseña_del_usuario():
    """
    Verifica que la contraseña del usuario sea hasheada correctamente.
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

    assert usuario_creado.password == "hashed_Password123!"

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
        email="a" * 250 + "@test.com",
        password="Password123!"
    )


    with pytest.raises(LongitudExcedida):
        await context.use_case().register(usuario, imagen=None)

@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_con_imagen():
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

@pytest.mark.asyncio
async def test_debe_utilizar_el_servicio_de_imagenes_cuando_se_envia_una_imagen():
    """
    Verifica que el servicio de imagen se llame correctamente durante el registro.
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

    await context.use_case().register(usuario, imagen=imagen)

    assert context.image_service.fue_llamado is True
    assert context.image_service.imagen_recibida == imagen
    assert context.image_service.servicio_recibido == "usuarios"


@pytest.mark.asyncio
async def test_debe_generar_un_correo_con_el_token_de_activacion():
    """
    Verifica que el servicio de correo se utilice correctamente durante el registro.
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

    assert context.mail_service.fue_llamado is True
    assert f"access_token_{usuario_creado.id_usuario}" in context.mail_service.cuerpo_html


@pytest.mark.asyncio
async def test_debe_generar_un_token_de_activacion():
    """
    Verifica que el servicio de token se utilice correctamente durante el registro.
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

    assert context.token_service.fue_llamado is True
    assert context.token_service.user_id_recibido == str(usuario_creado.id_usuario)
    assert context.token_service.access_token_generado == f"access_token_{usuario_creado.id_usuario}"

@pytest.mark.asyncio
async def test_debe_dar_error_al_incumplir_politica_de_contraseña():
    """
    Verifica que el servicio de política de contraseña se utilice correctamente durante el registro.
    """
    context = RegisterTestEnvironment()
    context.password_policy.es_valida = False

    usuario = UserRegisterDTO(
        email = "test@test.com",
        password = "Password123!"
    )

    with pytest.raises(ContraseñaNoSegura):
        await context.use_case().register(usuario, imagen=None)


@pytest.mark.asyncio
async def test_debe_dar_error_al_incumplir_politica_de_mail():
    """
    Verifica que el servicio de política de correo se utilice correctamente durante el registro.
    """
    context = RegisterTestEnvironment()
    context.mail_policy.es_valido = False

    usuario = UserRegisterDTO(
        email = "@test.com",
        password = "Password123!"
    )

    with pytest.raises(MailNoValido):
        await context.use_case().register(usuario, imagen=None)