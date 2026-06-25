from typing import Protocol, runtime_checkable

@runtime_checkable
class TokenProtocol(Protocol):

    def create_access_token(self, user_id: str) -> str:
        ...

    def get_user_id_from_access_token(self, token:str)->str:
        ...

    def get_user_id_from_refresh_token(self, token:str)->str:
        ...

    def create_refresh_token(self, user_id: str) -> str:
        ...
