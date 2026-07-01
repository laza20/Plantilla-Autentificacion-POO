from fastapi import Form, File, UploadFile
from src.auth.infrastructure.persistence.postgres.models import UserRegisterDTO

def parse_usuario_form(
    email: str = Form(...),
    password: str = Form(...),
    imagen: UploadFile | None = File(None)
) -> tuple[UserRegisterDTO, UploadFile | None]:

    usuario = UserRegisterDTO(
        email=email,
        password=password
    )

    return usuario, imagen

