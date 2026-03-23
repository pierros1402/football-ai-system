from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.users import User
from app.database import SessionLocal
from app.dependencies.auth_dependencies import admin_required
from app.services.auth_service import AuthService

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool
    is_email_verified: bool

    class Config:
        from_attributes = True


class PaginatedUsersResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[UserResponse]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/list", response_model=PaginatedUsersResponse)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("id"),
    order: Optional[str] = Query("asc"),
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    # Search σε username, email, full_name
    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.username.ilike(like))
            | (User.email.ilike(like))
            | (User.full_name.ilike(like))
        )

    # Sorting
    sortable_fields = {
        "id": User.id,
        "username": User.username,
        "email": User.email,
        "role": User.role,
    }
    sort_column = sortable_fields.get(sort, User.id)

    if order == "desc":
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)

    # Pagination
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return PaginatedUsersResponse(
        total=total,
        page=page,
        limit=limit,
        items=users,
    )


@router.post("/create")
def create_user(
    data: CreateUserRequest,
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = AuthService.hash_password(data.password)

    new_user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=hashed,
        role=data.role,
        is_active=True,
        is_email_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"detail": "User created successfully", "id": new_user.id}


@router.put("/update/{user_id}")
def update_user(
    user_id: int,
    data: UpdateUserRequest,
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email is not None:
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_email_verified is not None:
        user.is_email_verified = data.is_email_verified

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"detail": "User updated successfully"}


@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int,
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"detail": "User deleted successfully"}


@router.post("/force-verify/{user_id}")
def force_verify_user(
    user_id: int,
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_email_verified = True
    db.commit()

    return {"detail": "User email marked as verified"}


class AdminResetPasswordRequest(BaseModel):
    new_password: str


@router.post("/reset-password/{user_id}")
def admin_reset_password(
    user_id: int,
    data: AdminResetPasswordRequest,
    current_admin=Depends(admin_required),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = AuthService.hash_password(data.new_password)
    db.commit()

    return {"detail": "Password reset successfully by admin"}
