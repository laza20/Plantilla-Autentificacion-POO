from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado
from src.test.factories.factory_usuarios import crear_usuario_de_prueba
from src.test.fixtures.fixture_reenviar_mail import ReenviarMailTestEnvironment
import pytest



@pytest.mark.asyncio
async def test_debe_reenviar_el_mail_correctamente():
    context = ReenviarMailTestEnvironment()
    crear_usuario_de_prueba(context.auth_user_repository)

    resultado = await context.use_case().ejecutar("test@test.com")

    assert resultado["message"] == "Correo enviado correctamente"