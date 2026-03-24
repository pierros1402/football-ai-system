from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from app.models.users import User
from app.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------
    @staticmethod
    def authenticate_user(username: str, password: str):
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user

    # ---------------------------------------------------------
    # PASSWORD HASHING
    # ---------------------------------------------------------
    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str):
        return pwd_context.verify(plain, hashed)

    # ---------------------------------------------------------
    # ACCESS & REFRESH TOKENS
    # ---------------------------------------------------------
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token():
        payload = {
            "scope": "refresh_token",
            "exp": datetime.now(timezone.utc) + timedelta(days=30)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_refresh_token(token: str):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload.get("scope") == "refresh_token"
        except JWTError:
            return False

    @staticmethod
    def store_refresh_token(user: User, token: str):
        db = SessionLocal()
        user.refresh_token = token
        db.add(user)
        db.commit()
        db.close()

    @staticmethod
    def revoke_refresh_token(user: User):
        db = SessionLocal()
        user.refresh_token = None
        db.add(user)
        db.commit()
        db.close()

    # ---------------------------------------------------------
    # EMAIL VERIFICATION (JWT)
    # ---------------------------------------------------------
    @staticmethod
    def create_email_verification_token(user_id: int):
        payload = {
            "sub": str(user_id),
            "scope": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_email_token(token: str):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("scope") != "email_verification":
                return None

            return payload.get("sub")

        except JWTError:
            return None

    # ---------------------------------------------------------
    # PASSWORD RESET (JWT)
    # ---------------------------------------------------------
    @staticmethod
    def create_password_reset_token(user_id: int):
        payload = {
            "sub": str(user_id),
            "scope": "password_reset",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def reset_password(token: str, new_password: str):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("scope") != "password_reset":
                return False

            user_id = payload.get("sub")

            db = SessionLocal()
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                db.close()
                return False

            user.password_hash = pwd_context.hash(new_password)
            db.commit()
            db.close()
            return True

        except JWTError:
            return False
