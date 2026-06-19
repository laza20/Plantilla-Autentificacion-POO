from fastapi import Form, File, UploadFile
from src.auth.models import UserRegisterDTO

def parse_usuario_form(
    email: str = Form(...),
    password: str = Form(...),
    imagen_url: UploadFile | None = File(None)
    ) -> UserRegisterDTO:

    return UserRegisterDTO(
        email=email,
        password=password,
        imagen_url=imagen_url
    )

