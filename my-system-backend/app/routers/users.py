from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.user_service import UserService
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.admin_dependencies import admin_required

router = APIRouter()


# Dependency για DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Public route (δεν απαιτεί token)
@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return UserService.list_users(db)


# Protected route (απαιτεί JWT token)
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user


# 🔥 ADMIN‑ONLY ROUTE
@router.get("/admin/list")
def admin_list_users(
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    return UserService.list_users(db)
