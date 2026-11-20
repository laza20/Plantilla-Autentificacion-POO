from src.auth_core.domain.exceptions.domain import DomainError


class TokenException(DomainError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TokenExpirado(TokenException):
    def __init__(self, message: str = "El token que desea utilizar ha expirado"):
        super().__init__(message)


class VerificacionExpirada(TokenException):
    def __init__(self, message: str = "El enlace de verificación ha expirado"):
        super().__init__(message)


class TokenNoDesactivado(TokenException):
    def __init__(self, message: str = "El token no pudo ser desactivado"):
        super().__init__(message)


class TokenNoVerificado(TokenException):
    def __init__(self, message: str = "El token no pudo ser verificado correctamente."):
        super().__init__(message)


class TokenInvalido(TokenException):
    def __init__(self, message: str = "Token de ingreso invalido."):
        super().__init__(message)

class TokenResetInactivo(TokenException):
    def __init__(self, message: str = "Tu sesión de recuperación expiró, volvé a solicitar el link."):
        super().__init__(message)

class TokenVerificacionInactivo(TokenException):
    def __init__(self, message: str = "Tu sesión de verificación expiró, volvé a solicitar el link."):
        super().__init__(message)


class TokenReactivacionInactivo(TokenException):
    def __init__(self, message: str = "Tu sesión de reactivacion expiró, volvé a solicitar el link."):
        super().__init__(message)


class TokenEliminacionInactivo(TokenException):
    def __init__(self, message: str = "Tu token de eliminacion expiró."):
        super().__init__(message)

class VerificacionInvalida(TokenException):
    def __init__(self, message: str = "El usuario NO ah sido identificado con exito."):
        super().__init__(message)


class SinAccessToken(TokenException):
    def __init__(self, message: str = "No se proporcionó un token de acceso."):
        super().__init__(message)

class SinRefreshToken(TokenException):
    def __init__(self, message: str = "No se proporcionó un token de refresco."):
        super().__init__(message)


class SinResetToken(TokenException):
    def __init__(self, message: str = "No se proporcionó un token de restablecimiento."):
        super().__init__(message)