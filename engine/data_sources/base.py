from abc import ABC, abstractmethod
from typing import List
from engine.models.stats import MatchData, TeamData, PlayerData, EventData


class DataSource(ABC):
    """Abstract base class for any football data provider."""

    @abstractmethod
    def get_match(self, match_id: str) -> MatchData:
        ...

    @abstractmethod
    def get_team(self, team_id: str) -> TeamData:
        ...

    @abstractmethod
    def get_player(self, player_id: str) -> PlayerData:
        ...

    @abstractmethod
    def get_match_events(self, match_id: str) -> List[EventData]:
        ...

    @abstractmethod
    def get_league_matches(self, league_id: str, season: str) -> List[MatchData]:
        ...
