import logging
from fastapi import FastAPI
from app.routers.discovery import router as discovery_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()

app.include_router(discovery_router)
