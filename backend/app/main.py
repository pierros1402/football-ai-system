from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, auth, admin_users

app = FastAPI(
    title="My System API",
    description="Authentication with JWT Bearer tokens",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Routers with /api prefix
# -------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["Admin"])
