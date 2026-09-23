from slowapi import Limiter 
from slowapi.util import get_remote_address 
from src.config.config import Settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=Settings().RATE_LIMITER_ENABLED
)