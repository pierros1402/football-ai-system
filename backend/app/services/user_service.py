from sqlalchemy.orm import Session
from app.models.users import User

class UserService:

    @staticmethod
    def list_users(db: Session):
        return db.query(User).all()
