from fastapi import HTTPException, status

class DomainError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code or getattr(self, "status_code", 400)
        super().__init__(self.message)