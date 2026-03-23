from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.models.users import User
from app.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from app.services.email_service import EmailService

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="app/templates")


# -----------------------------
# Request Schemas
# -----------------------------

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RequestPasswordReset(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str


# -----------------------------
# Routes
# -----------------------------

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check username
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    hashed = AuthService.hash_password(data.password)

    # Create user
    new_user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=hashed,
        role="user",
        is_active=True,
        is_email_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create email verification token
    token = AuthService.create_email_verification_token(new_user.id)

    # Verification URL
    verify_url = f"http://localhost/api/auth/verify-email?token={token}"

    # Render HTML template
    html = templates.get_template("verify_email.html").render(
        verify_url=verify_url
    )

    # Send email
    EmailService.send_email(
        to_email=new_user.email,
        subject="Verify Your Email",
        html_content=html
    )

    return {"detail": "User registered. Please verify your email."}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user_id = AuthService.verify_email_token(token)

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_email_verified = True
    db.commit()

    return {"detail": "Email verified successfully"}


@router.post("/login")
def login(data: LoginRequest):
    user = AuthService.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = AuthService.create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role
    })

    refresh_token = AuthService.create_refresh_token()

    AuthService.store_refresh_token(user, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not AuthService.verify_refresh_token(data.refresh_token):
        raise HTTPException(status_code=401, detail="Expired or invalid refresh token")

    new_access_token = AuthService.create_access_token({"sub": user.username})
    new_refresh_token = AuthService.create_refresh_token()

    AuthService.store_refresh_token(user, new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    AuthService.revoke_refresh_token(current_user)
    return {"detail": "Logged out successfully"}


@router.post("/request-password-reset")
def request_password_reset(data: RequestPasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Δεν αποκαλύπτουμε αν υπάρχει ή όχι
    if not user:
        return {"detail": "If this email exists, a reset link has been sent."}

    token = AuthService.create_password_reset_token(user.id)

    reset_url = f"https://myapp.com/reset-password?token={token}"

    html = templates.get_template("reset_password_email.html").render(
        reset_url=reset_url
    )

    EmailService.send_email(
        to_email=user.email,
        subject="Password Reset",
        html_content=html
    )

    return {"detail": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPassword):
    ok = AuthService.reset_password(data.token, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"detail": "Password reset successfully"}
