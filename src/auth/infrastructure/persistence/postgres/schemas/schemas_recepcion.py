from pydantic import BaseModel, EmailStr

class SolicitudRecuperacionRequest(BaseModel):
    email: EmailStr

class SolicitudReactivacionRequest(BaseModel):
    email: EmailStr


class ModificarPassword(BaseModel):
    password: str