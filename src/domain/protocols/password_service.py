from typing import Protocol, runtime_checkable

@runtime_checkable
class PasswordProtocol(Protocol):

    def hash_password(self, password: str) -> str:
        ...

    def verify_password(self, plain: str, hashed: str) -> bool:
        ...
