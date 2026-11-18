from typing import Protocol, BinaryIO

class TipadoImagenProtocol(Protocol):

    @property
    def filename(self) -> str | None: 
        ...

    @property
    def size(self) -> int | None: 
        ...

    @property
    def file(self) -> BinaryIO: 
        ...