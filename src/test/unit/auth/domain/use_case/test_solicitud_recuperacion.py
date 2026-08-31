from src.test.fixtures.fixture_solicitud_recuperacion_contraseña import SolicitudRecuperacionContraseñaTestEnvironment
import pytest
from src.test.factories.factory_usuarios import crear_usuario_de_prueba

@pytest.mark.asyncio
async def test_debe_registrar_un_usuario_valido_sin_imagen():
    """
    Verifica que un usuario sea registrado correctamente con datos válidos.
    """
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    resultado = await context.use_case().ejecutar(
        usuario.email
    )

    assert resultado["message"] == "Mail enviado correctamente, revise su bandeja de entrada, si no lo encuentra revise en spam o correos no deseados."