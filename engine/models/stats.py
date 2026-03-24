from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class TeamData:
    id: str
    name: str
    short_name: Optional[str]
    country: Optional[str]


@dataclass
class PlayerData:
    id: str
    name: str
    position: Optional[str]
    shirt_number: Optional[int]
    team_id: Optional[str]


@dataclass
class MatchData:
    id: str
    home_team: TeamData
    away_team: TeamData
    kickoff_time: datetime
    status: str  # "scheduled", "live", "finished"
    home_score: Optional[int]
    away_score: Optional[int]
    league_name: Optional[str]
    season: Optional[str]


@dataclass
class EventData:
    id: str
    match_id: str
    minute: int
    second: int
    type: str  # "goal", "card", "substitution", etc.
    team_id: Optional[str]
    player_id: Optional[str]
    description: Optional[str]
