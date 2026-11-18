class DomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SinCargas(DomainError):
    def __init__(self, message: str = "No se han realizado cargas."):
        super().__init__(message)


class LongitudExcedida(DomainError):
    def __init__(
        self,
        message: str = "Uno o más campos exceden el límite de caracteres permitido."
    ):
        super().__init__(message)


class LimiteTamañoSuperado(DomainError):
    def __init__(
        self,
        message: str = "El tamaño de la imagen excede el límite permitido."
    ):
        super().__init__(message)


class ExtensionNoPermitida(DomainError):
    def __init__(
        self,
        message: str = "La extensión del archivo no está permitida."
    ):
        super().__init__(message)


class ErrorCloudinary(DomainError):
    def __init__(
        self,
        error: str,
        message: str = "Error al subir la imagen a Cloudinary."
    ):
        full_message = f"{message} Detalles del error: {error}"
        super().__init__(full_message)


class ErrorCreacion(DomainError):
    def __init__(
        self,
        message: str = "No se pudo crear de manera correcta el registro."
    ):
        super().__init__(message)


class ErrorEliminacion(DomainError):
    def __init__(
        self,
        message: str = "No se pudo eliminar de manera correcta el registro."
    ):
        super().__init__(message)