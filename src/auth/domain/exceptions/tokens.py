from src.auth.domain.exceptions.domain import DomainError
from fastapi import status

class TokenException(DomainError):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code or getattr(self, "status_code", 400)
        super().__init__(self.message)


class TokenExpirado(TokenException): 
    status_code = status.HTTP_403_FORBIDDEN
    def __init__(self, message: str = "El token que desea utilizar a expirado"):
        super().__init__(message)

class VerificacionExpirada(TokenException): 
    status_code = status.HTTP_403_FORBIDDEN
    def __init__(self, message: str = "El enlace de verificación ha expirado"):
        super().__init__(message)

class TokenNoDesactivado(TokenException): 
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "El token no pudo ser desactivado"):
        super().__init__(message)

class TokenNoVerificado(TokenException): 
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "El token no pudo ser verificado correctamente."):
        super().__init__(message)


class TokenInvalido(TokenException):
    status_code = status.HTTP_401_UNAUTHORIZED
    def __init__(self, message: str = "Token de ingreso invalido."):
        super().__init__(message)


class VerificacionInvalida(TokenException):
    status_code = status.HTTP_401_UNAUTHORIZED
    def __init__(self, message: str = "El usuario NO ah sido identificado con exito."):
        super().__init__(message)