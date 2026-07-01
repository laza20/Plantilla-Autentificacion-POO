from src.auth.domain.exceptions.domain import DomainError

class UsuarioError(DomainError):
    status_code = 400
    pass

class LoginError(UsuarioError):
    status_code = 400
    pass

class UsuarioNoEncontrado(UsuarioError):
    status_code = 409
    pass

class NoAutenticado(UsuarioError):
    status_code = 401
    pass

class SinAccessToken(UsuarioError):
    status_code = 401
    pass

class SinRefreshToken(UsuarioError):
    status_code = 401
    pass

class TokenInvalido(UsuarioError):
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

