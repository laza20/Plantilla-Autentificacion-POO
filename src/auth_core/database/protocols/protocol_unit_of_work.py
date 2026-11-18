from typing import Protocol, runtime_checkable

@runtime_checkable
class UnitOfWorkProtocol(Protocol):
    """
    Contrato de contexto transaccional (`with`) para agrupar inserts/updates/
    deletes de un caso de uso en una sola unidad atómica: commit al salir
    sin excepción, rollback si se propaga una.
    """
    def __enter__(self):pass

    def __exit__(self, exc_type, exc, tb):pass