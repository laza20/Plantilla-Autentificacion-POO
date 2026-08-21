from src.auth.domain.exceptions.domain import DomainError
from fastapi import status

class UsuarioError(DomainError):
    status_code = 400
    pass

class LoginError(UsuarioError):
    status_code = 400
    pass

class UsuarioNoModificado(UsuarioError): 
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "No se pudo modificar la contraseña"):
        super().__init__(message)


class UsuarioNoEncontrado(UsuarioError):
    status_code = 409
    pass

class UsuarioActivo(UsuarioError):
    status_code = 400

class NoAutenticado(UsuarioError):
    status_code = 401
    pass

class SinAccessToken(UsuarioError):
    status_code = 401
    pass

class SinRefreshToken(UsuarioError):
    status_code = 401
    pass


class UsuariosNoEncontrados(UsuarioError):
    status_code = 409
    pass


class ResultadoInvalido(DomainError):
    status_code = 409
    pass

class AvatarError(UsuarioError):
    status_code = 409
    pass

class TiempoInterrupcionInicioSesion(UsuarioError):
    status_code = 403
    pass


class UsuarioInactivo(UsuarioError):
    status_code = 423
    pass

