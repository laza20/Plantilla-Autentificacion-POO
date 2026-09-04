from datetime import datetime, timedelta, timezone

def crear_recover_password_de_prueba(
    recuperar_contraseña_repository,
    id_usuario: int = 1,
    token_hash: str = "hashed_1a2s3w5e6g9s8d5c5d6s5c5s5d5s69s7",
    expira_en= datetime.now(timezone.utc) + timedelta(minutes=15)
):
    return recuperar_contraseña_repository.insertar_recuperacion_contraseña(
        id_usuario=id_usuario,
        token_hash=token_hash,
        expira_en=expira_en
    )
