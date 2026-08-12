from src.auth.infrastructure.persistence.postgres.models_auth_users import AuthUser

def crear_usuario_de_prueba(
    auth_user_repository,
    email="test@test.com",
    password="hashed_password@123",
    imagen_url=None
):
    usuario_existente = AuthUser(
        email=email,
        password=password,
        imagen_url=imagen_url
    )
    return auth_user_repository.insertar(usuario_existente)
