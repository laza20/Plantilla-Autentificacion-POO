from fastapi import Form, File, UploadFile
from src.auth.infrastructure.persistence.postgres.models.models_auth_users import UserRegisterDTO, UserModifyDTO

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


def parse_modificar_usuario_form(
    email: str | None = Form(None),
    imagen: UploadFile | None = File(None)
) -> tuple[UserModifyDTO, UploadFile | None]:

    usuario = UserModifyDTO(
        email=email
    )

    return usuario, imagen

