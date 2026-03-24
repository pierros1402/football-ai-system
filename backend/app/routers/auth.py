from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from ..auth.dependencies import get_current_user, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# REGISTER
@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_admin=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# LOGIN (email OR username)
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username can be email OR username
    user = (
        db.query(User)
        .filter(
            (User.email == form_data.username)
            | (User.username == form_data.username)
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# GET CURRENT USER
@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# REFRESH TOKEN
@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        user_id = decode_token(refresh_token)
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }
