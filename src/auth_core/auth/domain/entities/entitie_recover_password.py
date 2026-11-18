from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RecoverPassword:
    token_hash: str
    id_usuario: int
    id_recover_password: Optional[int] = None
    expira_en: Optional[datetime] = None
    usado: bool = False