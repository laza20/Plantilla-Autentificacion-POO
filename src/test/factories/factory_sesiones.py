def crear_sesion_de_prueba(
    token_repository,
    id_usuario: int = 1,
    hash_token: str = "hash_token_1",
    ip: str = "127.0.0.1",
    user_agent: str = "user_agent_1",
):
    return token_repository.insertar_sesion(
        hash_token=hash_token,
        id_usuario=id_usuario,
        ip=ip,
        user_agent=user_agent,
    )