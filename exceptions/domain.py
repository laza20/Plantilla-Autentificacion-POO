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
