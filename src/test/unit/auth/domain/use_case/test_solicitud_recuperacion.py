from src.test.fixtures.fixture_solicitud_recuperacion_contraseña import SolicitudRecuperacionContraseñaTestEnvironment
import pytest
from src.test.factories.factory_usuarios import crear_usuario_de_prueba

@pytest.mark.asyncio
async def test_debe_realizar_la_solicitud_de_recuperacion_de_manera_correcta():
    """
    Realiza la peticion para reestablecer una contraseña de manera correcta.
    """
    context = SolicitudRecuperacionContraseñaTestEnvironment()

    usuario = crear_usuario_de_prueba(context.auth_user_repository)

    resultado = await context.use_case().ejecutar(
        usuario.email
    )

    assert resultado["message"] == "Mail enviado correctamente, revise su bandeja de entrada, si no lo encuentra revise en spam o correos no deseados."
