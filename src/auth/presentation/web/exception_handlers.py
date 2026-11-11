from fastapi import status
from src.auth.domain.exceptions.tokens import (
    TokenException,
    TokenExpirado,
    TokenNoDesactivado,
    TokenNoVerificado,
    TokenInvalido,
    TokenResetInactivo,
    TokenVerificacionInactivo,
    TokenReactivacionInactivo,
    TokenEliminacionInactivo,
    VerificacionInvalida,
    VerificacionExpirada,
)
from src.auth.domain.exceptions.usuarios_exceptions import (
    UsuarioError,
    UsuarioNoModificado,
    UsuarioNoEliminado,
    PeriodoReactivacionFinalizado,
    MailRepetido,
    UsuarioNoEncontrado,
    NoAutenticado,
    SinAccessToken,
    SinRefreshToken,
    UsuariosNoEncontrados,
    ContraseñaNoSegura,
    MailNoValido,
    UsuarioActivo
)
from src.domain.exceptions.domain import (
    DomainError,
    SinCargas,
    LongitudExcedida,
    LimiteTamañoSuperado,
    ExtensionNoPermitida,
    ErrorCloudinary,
    ErrorCreacion,
    ErrorEliminacion,
)

HTTP_STATUS_BY_EXCEPTION = {
    DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,

    SinCargas: status.HTTP_409_CONFLICT,
    LongitudExcedida: status.HTTP_422_UNPROCESSABLE_CONTENT,
    LimiteTamañoSuperado: status.HTTP_413_CONTENT_TOO_LARGE,
    ExtensionNoPermitida: status.HTTP_400_BAD_REQUEST,
    ErrorCloudinary: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCreacion: status.HTTP_409_CONFLICT,
    ErrorEliminacion: status.HTTP_409_CONFLICT,
    # Clases padre: valores por defecto
    UsuarioError: status.HTTP_400_BAD_REQUEST,
    TokenException: status.HTTP_400_BAD_REQUEST,

    # Excepciones de tokens
    TokenExpirado: status.HTTP_403_FORBIDDEN,
    VerificacionExpirada: status.HTTP_403_FORBIDDEN,
    TokenNoDesactivado: status.HTTP_409_CONFLICT,
    TokenNoVerificado: status.HTTP_409_CONFLICT,
    TokenInvalido: status.HTTP_401_UNAUTHORIZED,
    TokenResetInactivo: status.HTTP_401_UNAUTHORIZED,
    TokenVerificacionInactivo: status.HTTP_401_UNAUTHORIZED,
    TokenReactivacionInactivo: status.HTTP_401_UNAUTHORIZED,
    TokenEliminacionInactivo: status.HTTP_401_UNAUTHORIZED,
    VerificacionInvalida: status.HTTP_401_UNAUTHORIZED,

    # Excepciones de usuarios
    UsuarioNoModificado: status.HTTP_409_CONFLICT,
    UsuarioNoEliminado: status.HTTP_409_CONFLICT,
    PeriodoReactivacionFinalizado: status.HTTP_409_CONFLICT,
    MailRepetido: status.HTTP_409_CONFLICT,
    UsuarioNoEncontrado: status.HTTP_409_CONFLICT,
    UsuariosNoEncontrados: status.HTTP_409_CONFLICT,
    ContraseñaNoSegura: status.HTTP_400_BAD_REQUEST,
    MailNoValido: status.HTTP_400_BAD_REQUEST,
    UsuarioActivo: status.HTTP_400_BAD_REQUEST,
    NoAutenticado: status.HTTP_401_UNAUTHORIZED,
    SinAccessToken: status.HTTP_401_UNAUTHORIZED,
    SinRefreshToken: status.HTTP_401_UNAUTHORIZED
}


def obtener_status_code(exc: Exception) -> int:
    for clase in type(exc).__mro__:
        if clase in HTTP_STATUS_BY_EXCEPTION:
            return HTTP_STATUS_BY_EXCEPTION[clase]

    return status.HTTP_500_INTERNAL_SERVER_ERROR