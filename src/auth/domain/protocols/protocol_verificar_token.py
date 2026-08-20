from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class VerificarTokenProtocol(Protocol):
  def verificar_token(self, token_recuperacion:str, id_usuario:int, fecha_actual:datetime)->bool:pass