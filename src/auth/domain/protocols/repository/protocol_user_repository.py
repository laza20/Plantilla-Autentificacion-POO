from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models.models_usuario import Usuario

@runtime_checkable
class UsuarioRepositoryProtocol(Protocol):
    """Contrato de persistencia para la tabla `usuario`.

    `usuario` es el modelo secundario de datos de negocio de un usuario
    autenticado (ej. nombre, apellido), relacionado 1 a 1 con `auth_user`
    reutilizando `id_usuario` como PK y FK (sin id propio), con
    ON DELETE CASCADE. Separado de `AuthUserRepositoryProtocol`, que
    maneja exclusivamente los datos de autenticación.
    """

    def insertar(self, usuario: Usuario) -> Usuario:
        """Persiste un nuevo registro en `usuario`.

        Se espera que `usuario.id_usuario` ya exista como PK en `auth_user`
        (típicamente insertado en el mismo Unit of Work que RegisterUseCase,
        tras el flush() del id generado por auth_user_repository).

        Args:
            usuario: Instancia a persistir, con id_usuario ya asignado.

        Returns:
            El usuario persistido.
        """
        ...