from src.auth.infrastructure.persistence.postgres.models_sesiones import Sesiones
from sqlalchemy.orm import Session
from datetime import datetime


class HistoryPasswordRepository:
    def __init__(self, session: Session):
        self.session = session


