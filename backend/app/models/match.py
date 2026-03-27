from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    start_timestamp = Column(Integer)
    status = Column(String)
    round = Column(String)
    venue = Column(String)
    home_team_id = Column(Integer)
    away_team_id = Column(Integer)
    score_home = Column(Integer)
    score_away = Column(Integer)
    json_data = Column(JSON)
