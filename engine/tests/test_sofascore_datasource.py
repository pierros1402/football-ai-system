import pytest
from datetime import datetime

from engine.data_sources.sofascore import SofascoreDataSource
from engine.models.stats import MatchData, TeamData, PlayerData, EventData


class DummySofascore(SofascoreDataSource):
    def __init__(self, fake_responses: dict):
        super().__init__(session=None)
        self.fake_responses = fake_responses

    def _get(self, path: str, params=None) -> dict:
        return self.fake_responses[path]


def test_get_match_maps_basic_fields():
    fake_match = {
        "event": {
            "id": 123,
            "homeTeam": {"id": 1, "name": "Home FC"},
            "awayTeam": {"id": 2, "name": "Away FC"},
            "startTimestamp": 1700000000,
            "status": {"type": "finished"},
            "homeScore": {"current": 2},
            "awayScore": {"current": 1},
            "tournament": {"name": "Premier League"},
            "season": {"name": "2024/2025"},
        }
    }

    ds = DummySofascore(fake_responses={"/event/123": fake_match})
    match = ds.get_match("123")

    assert isinstance(match, MatchData)
    assert match.id == "123"
    assert match.home_team.name == "Home FC"
    assert match.away_team.name == "Away FC"
    assert match.home_score == 2
    assert match.away_score == 1
    assert match.league_name == "Premier League"
    assert match.season == "2024/2025"
    assert match.status == "finished"
    assert isinstance(match.kickoff_time, datetime)


def test_get_team_maps_basic_fields():
    fake_team = {
        "team": {
            "id": 10,
            "name": "Test Team",
            "shortName": "TT",
            "country": {"name": "Greece"},
        }
    }

    ds = DummySofascore(fake_responses={"/team/10": fake_team})
    team = ds.get_team("10")

    assert isinstance(team, TeamData)
    assert team.id == "10"
    assert team.name == "Test Team"
    assert team.short_name == "TT"
    assert team.country == "Greece"


def test_get_player_maps_basic_fields():
    fake_player = {
        "player": {
            "id": 99,
            "name": "Test Player",
            "position": "FW",
            "shirtNumber": 9,
            "team": {"id": 10},
        }
    }

    ds = DummySofascore(fake_responses={"/player/99": fake_player})
    player = ds.get_player("99")

    assert isinstance(player, PlayerData)
    assert player.id == "99"
    assert player.name == "Test Player"
    assert player.position == "FW"
    assert player.shirt_number == 9
    assert player.team_id == "10"


def test_get_match_events_maps_basic_fields():
    fake_incidents = {
        "incidents": [
            {
                "id": 1,
                "time": {"minute": 10, "second": 5},
                "incidentType": "goal",
                "team": {"id": 1},
                "player": {"id": 99},
                "text": "Goal by Test Player",
            }
        ]
    }

    ds = DummySofascore(fake_responses={"/event/123/incidents": fake_incidents})
    events = ds.get_match_events("123")

    assert len(events) == 1
    ev = events[0]
    assert isinstance(ev, EventData)
    assert ev.match_id == "123"
    assert ev.minute == 10
    assert ev.second == 5
    assert ev.type == "goal"
    assert ev.team_id == "1"
    assert ev.player_id == "99"
    assert ev.description == "Goal by Test Player"
