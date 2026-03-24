from fastapi import FastAPI
from .config import settings
from .routers import auth

app = FastAPI(title=settings.app_name)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
