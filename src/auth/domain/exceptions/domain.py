from fastapi import HTTPException, status

class DomainError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code or getattr(self, "status_code", 400)
        super().__init__(self.message)

class ContraseñaNoSegura(DomainError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str = "La contraseña no cumple con los requisitos de seguridad."):
        super().__init__(message)


class SinCargas(DomainError):
    status_code = status.HTTP_409_CONFLICT
    
    def __init__(self, message: str = "No se han realizado cargas."):
        super().__init__(message)

class LongitudExcedida(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    def __init__(self, message: str = "Uno o más campos exceden el límite de caracteres permitido."):
        super().__init__(message)


class LimiteTamañoSuperado(DomainError):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    def __init__(self, message: str = "El tamaño de la imagen excede el límite permitido."):
        super().__init__(message)

class ExtensionNoPermitida(DomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    def __init__(self, message: str = "La extensión del archivo no está permitida."):
        super().__init__(message)

class ErrorCloudinary(DomainError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    def __init__(self, error: str, message: str = "Error al subir la imagen a Cloudinary."):
        full_message = f"{message} Detalles del error: {error}"
        super().__init__(full_message)