from src.domain.exceptions.domain import DomainError
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

class UsuarioNoEliminado(UsuarioError): 
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "El usuario que desea reactivar no esta eliminado."):
        super().__init__(message)

class PeriodoReactivacionFinalizado(UsuarioError): 
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "La cuenta que desea reactivar ya cumplio su posible tiempo de reactivacion."):
        super().__init__(message)

class ContraseñaNoSegura(UsuarioError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str = """La contraseña no cumple con los requisitos de seguridad. Debe contener al menos:        
                - Al menos 8 caracteres
                - Al menos una letra mayúscula
                - Al menos una letra minúscula
                - Al menos un número
                - Al menos un carácter especial"""):
        super().__init__(message)

class MailNoValido(UsuarioError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str = """El mail no cumple con los requisitos de seguridad. Debe contener al menos:
                - debe tener un solo arroba.
                - debe tener un punto luego del arroba.
                - debe tener una separacion por caracteres entre el punto y el arroba.
                - debe tener al menos 6 caracteres."""):
        super().__init__(message)

class MailRepetido(UsuarioError):
    status_code = status.HTTP_409_CONFLICT
    def __init__(self, message: str = "El correo electrónico ya está en uso."):
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

