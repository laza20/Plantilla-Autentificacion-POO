from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario

@runtime_checkable
class UsuarioRepositoryProtocol(Protocol):
    
    def insertar(self, usuario: Usuario) -> Usuario: ...