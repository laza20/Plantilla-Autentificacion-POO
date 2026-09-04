from src.auth.domain.exceptions.tokens import VerificacionInvalida, TokenInvalido
import pytest
from src.test.fixtures.fixture_verify_mail_case import VerifyEmailTestEnvironment
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import AuthUser
from src.auth.domain.exceptions.usuarios_exceptions import UsuarioNoEncontrado, UsuarioActivo
from src.database.enums.estado_entidad import EstadoEntidad


def test_debe_verificar_el_mail_y_activar_el_usuario():
    """
    Verifica que un usuario pueda activar su cuenta mediante un token válido.

    El caso de uso debe:
    - verificar que el usuario exista.
    - validar el token recibido.
    - marcar al usuario como verificado y activo.
    """
    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.auth_user_repository.insertar(usuario_existente)
    context.use_case().ejecutar(
        token=f"verificacion_token_{usuario.id_usuario}"
    )
    usuario_activado = context.auth_user_repository.obtener_por_email("test@test.com")

    assert usuario_activado.estado == EstadoEntidad.ACTIVO
    assert usuario_activado.is_verified is True
    assert context.token_service.user_id_recibido == usuario.id_usuario


def test_debe_verificar_que_los_tokens_sean_adecuados():
    """
    Verifica que los tokens recibidos sean adeacuados en referencia a los tokens generados.
    """
    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.auth_user_repository.insertar(usuario_existente)
    tokens = context.use_case().ejecutar(token= f"verificacion_token_{usuario.id_usuario}")

    assert tokens.access_token == context.token_service.access_token_generado
    assert tokens.refresh_token == context.token_service.refresh_token_generado




def test_debe_verificar_que_da_error_de_tipo_token_invalido_cuando_no_coincide_los_id():
    """
    El test se debe encargar de generar un error cuando el user_id no coincide con 
    lo que debe coincidir.
    """

    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.auth_user_repository.insertar(usuario_existente)

    with pytest.raises(TokenInvalido):
        context.use_case().ejecutar(        
            token="verificacion_token_"
            )

def test_debe_dar_error_cuando_no_se_encuentra_el_usuario():
    """
    El test genera un error del tipo UsuarioNoEncontrado cuando el token que se utiliza no tiene 
    usuario para el id asociado.
    """
    context = VerifyEmailTestEnvironment()

    with pytest.raises(UsuarioNoEncontrado):
        context.use_case().ejecutar(        
            token="verificacion_token_1"
            )

def test_debe_dar_error_cuando_el_usuario_que_se_quiere_activar_ya_esta_activo():
    """
    El error se produce cuando al intentarse buscar el usuario por medio del metodo 
    obtener_por_id_sin_activar, el usuario se encuentra pero ya esta activo.
    """
    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123",
        estado=EstadoEntidad.ACTIVO
    )

    usuario = context.auth_user_repository.insertar(usuario_existente)
    with pytest.raises(UsuarioActivo):
        context.use_case().ejecutar(        
            token=f"verificacion_token_{usuario.id_usuario}"
            )


@pytest.mark.parametrize(
    "token",
    [
        "",
        "hola",
        "verificacion",
        "verificacion_token",
        "refresh_token_1",
        "token_hola_1",
        "hola_token_1",
        "_verificacion_token_1",
        "verificacion_token_",
    ],
)
def test_debe_dar_error_cuando_el_formato_del_token_es_invalido(token):
    """
    Verifica que cualquier token con un formato inválido produzca
    una excepción VerificacionInvalida.
    """
    context = VerifyEmailTestEnvironment()

    with pytest.raises(TokenInvalido):
        context.use_case().ejecutar(
            token=token
        )