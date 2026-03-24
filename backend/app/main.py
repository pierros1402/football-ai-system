from fastapi import FastAPI
from .config import settings
from .routers import auth
from .database import Base, engine
from . import models

Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.app_name)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
