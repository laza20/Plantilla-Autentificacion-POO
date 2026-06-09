from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from src.database.client import engine
from exceptions.domain import DomainError
from fastapi.responses import JSONResponse

SQLModel.metadata.create_all(engine)
app = FastAPI()

from src.auth import(routers as usuarios)

app.include_router(usuarios.router)



@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
