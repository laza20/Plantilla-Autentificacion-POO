from fastapi import Depends
from src.auth.repository import (UserRepository, get_user_repository)
from src.config.config import (Settings, get_settings)
from src.container.auth_container import AuthContainer
from src.auth.service import AuthService


def get_auth_service(
    settings: Settings = Depends(get_settings),
    repository: UserRepository = Depends(get_user_repository)
) -> AuthService:

    return AuthContainer(settings, repository).auth_service