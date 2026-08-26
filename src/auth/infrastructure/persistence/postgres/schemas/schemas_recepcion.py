from pydantic import BaseModel, EmailStr

class SolicitudRecuperacionRequest(BaseModel):
    email: EmailStr


class ModificarPassword(BaseModel):
    password: str