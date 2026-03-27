from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from app.db.base import Base

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    name = Column(String)
    year = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    json_data = Column(JSON)
