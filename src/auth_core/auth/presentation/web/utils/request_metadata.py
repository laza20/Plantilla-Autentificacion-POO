from fastapi import Request

class RequestMetadata:
    def __init__(self, request: Request):
        self.request = request

    def get_ip(self) -> str:
        x_forwarded_for = self.request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return self.request.client.host

    def get_user_agent(self) -> str:
        return self.request.headers.get("user-agent", "Desconocido")