from src.auth.domain.exceptions.tokens import VerificacionInvalida
import pytest
from src.test.fixtures.fixture_verify_mail_case import VerifyEmailTestEnvironment
from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser
from fastapi import Response
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

    usuario = context.repository.insertar(usuario_existente)
    context.use_case().verificar_mail(
        token=f"access_token_{usuario.id_usuario}",
        response=Response()
    )
    usuario_activado = context.repository.obtener_por_email("test@test.com")

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

    usuario = context.repository.insertar(usuario_existente)
    tokens = context.use_case().verificar_mail(token= f"access_token_{usuario.id_usuario}", response= Response())

    assert tokens.access_token == context.token_service.access_token_generado
    assert tokens.refresh_token == context.token_service.refresh_token_generado


def test_debe_verificar_que_se_llama_al_servicio_de_cookies():
    """
    El test se debe encargar de verificar que en el flujo de la activacion de la cuenta por medio
    del mail enviado, las cookies se setean correctamente, en este caso el stub, que solo realiza
    modificaciones de los parametros.
    """

    context = VerifyEmailTestEnvironment()

    usuario_existente = AuthUser(
        email="test@test.com",
        password="hashed_password@123"
    )

    usuario = context.repository.insertar(usuario_existente)
    context.use_case().verificar_mail(
        token=f"access_token_{usuario.id_usuario}",
        response=Response()
    )

    assert context.cookies_service.fue_llamado is True
    assert context.cookies_service.access_token == f"access_token_{usuario.id_usuario}"
    assert context.cookies_service.refresh_token is not None



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

    usuario = context.repository.insertar(usuario_existente)

    with pytest.raises(VerificacionInvalida):
        context.use_case().verificar_mail(        
            token="access_token_",
            response=Response()
            )

def test_debe_dar_error_cuando_no_se_encuentra_el_usuario():
    """
    El test genera un error del tipo UsuarioNoEncontrado cuando el token que se utiliza no tiene 
    usuario para el id asociado.
    """
    context = VerifyEmailTestEnvironment()

    with pytest.raises(UsuarioNoEncontrado):
        context.use_case().verificar_mail(        
            token="access_token_1",
            response=Response()
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

    usuario = context.repository.insertar(usuario_existente)
    with pytest.raises(UsuarioActivo):
        context.use_case().verificar_mail(        
            token=f"access_token_{usuario.id_usuario}",
            response=Response()
            )


@pytest.mark.parametrize(
    "token",
    [
        "",
        "hola",
        "access",
        "access_token",
        "refresh_token_1",
        "token_hola_1",
        "hola_token_1",
        "_access_token_1",
        "access_token_",
    ],
)
def test_debe_dar_error_cuando_el_formato_del_token_es_invalido(token):
    """
    Verifica que cualquier token con un formato inválido produzca
    una excepción VerificacionInvalida.
    """
    context = VerifyEmailTestEnvironment()

    with pytest.raises(VerificacionInvalida):
        context.use_case().verificar_mail(
            token=token,
            response=Response(),
        )