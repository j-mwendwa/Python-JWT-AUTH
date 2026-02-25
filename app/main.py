from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as user_router
from app.database.base import Base
from app.database.engine import engine
from app.models.user import User  # noqa: F401

app = FastAPI(title="JWT Auth API")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(user_router)
