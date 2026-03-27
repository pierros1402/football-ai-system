from sqlalchemy import Column, Integer, String, JSON
from app.db.base import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    country = Column(String)
    type = Column(String)
    priority = Column(Integer)
    json_data = Column(JSON)
