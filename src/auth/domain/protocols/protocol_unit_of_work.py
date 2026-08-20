from typing import Protocol, runtime_checkable

@runtime_checkable
class UnitOfWork(Protocol):
    def __enter__(self):pass

    def __exit__(self, exc_type, exc, tb):pass