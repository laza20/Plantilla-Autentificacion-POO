from fastapi import Form, File, UploadFile
from datetime import date
from typing import Optional

async def parse_usuario_form(
    email: str = Form(...),
    password: str = Form(...),
    imagen_url: Optional[UploadFile] = File(default=None)
):
    return {
        "email": email,
        "password": password,
        "imagen_url": imagen_url,
    }