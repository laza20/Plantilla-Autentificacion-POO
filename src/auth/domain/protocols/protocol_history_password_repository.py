from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class HistoryRepositoryProtocol(Protocol):
  def insertar_history_repository(
      self, 
      id_usuario:int, 
      password_hash_anterior:str, 
      fecha_cambio:datetime)->bool:pass