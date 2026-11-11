from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.domain import DomainError
from src.auth.presentation.web.exception_handlers import obtener_status_code
from src.auth.presentation.web import routers as usuarios

from src.auth.infrastructure.persistence.postgres.models import *

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.shared.infrastructure.security.rate_limiter.limiter import limiter


app = FastAPI()

app.include_router(usuarios.router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=obtener_status_code(exc),
        content={"detail": exc.message}
    )