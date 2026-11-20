from src.auth_core.domain.exceptions.domain import DomainError


class UsuarioError(DomainError):
    def __init__(self, message: str = "Ocurrió un error con el usuario."):
        super().__init__(message)


class LoginError(UsuarioError):
    def __init__(self, message: str = "Ocurrio un error al iniciar sesión."):
        super().__init__(message)


class UsuarioNoEncontrado(UsuarioError):
    def __init__(self, message: str = "No se pudo encontrar el usuario."):
        super().__init__(message)


class MailRepetido(UsuarioError):
    def __init__(self, message: str = "El correo electrónico ya está en uso."):
        super().__init__(message)


class UsuarioNoModificado(UsuarioError): 
    def __init__(self, message: str = "No se pudo modificar la contraseña"):
        super().__init__(message)

class UsuarioNoEliminado(UsuarioError): 
    def __init__(self, message: str = "El usuario que desea reactivar no esta eliminado."):
        super().__init__(message)

class PeriodoReactivacionFinalizado(UsuarioError): 
    def __init__(self, message: str = "La cuenta que desea reactivar ya cumplio su posible tiempo de reactivacion."):
        super().__init__(message)

class ContraseñaNoSegura(UsuarioError):
    def __init__(self, message: str = """La contraseña no cumple con los requisitos de seguridad. Debe contener al menos:        
                - Al menos 8 caracteres
                - Al menos una letra mayúscula
                - Al menos una letra minúscula
                - Al menos un número
                - Al menos un carácter especial"""):
        super().__init__(message)

class MailNoValido(UsuarioError):
    def __init__(self, message: str = """El mail no cumple con los requisitos de seguridad. Debe contener al menos:
                - debe tener un solo arroba.
                - debe tener un punto luego del arroba.
                - debe tener una separacion por caracteres entre el punto y el arroba.
                - debe tener al menos 6 caracteres."""):
        super().__init__(message)


class UsuarioActivo(UsuarioError):
    def __init__(self, message: str = "El usuario ya está activo."):
        super().__init__(message)


class NoAutenticado(UsuarioError):
    def __init__(self, message: str = "El usuario no está autenticado."):
        super().__init__(message)


class UsuariosNoEncontrados(UsuarioError):
    def __init__(self, message: str = "No se encontraron usuarios."):
        super().__init__(message)