from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HistoryPassword:
    password_hash_anterior: str
    id_usuario: int
    id_history_password: Optional[int] = None
    fecha_cambio: Optional[datetime] = None