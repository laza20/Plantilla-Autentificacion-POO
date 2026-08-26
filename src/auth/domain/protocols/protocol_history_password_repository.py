from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class HistoryRepositoryProtocol(Protocol):
  def insertar_history_repository(
      self, 
      id_usuario:int, 
      password_hash_anterior:str, 
      fecha_cambio:datetime)->bool:
      """
      Permite insertar dentro de la tabla de history password repository, esta tabla permite llevar una correlacion de
      las contraseñas de los usuarios.
      """

      pass
  