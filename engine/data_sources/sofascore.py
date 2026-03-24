from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import requests

from engine.data_sources.base import DataSource
from engine.models.stats import MatchData, TeamData, PlayerData, EventData


class SofascoreDataSource(DataSource):
    """
    Sofascore-based data source.

    NOTE: Τα ακριβή endpoints μπορεί να χρειαστούν fine-tuning,
    αλλά το interface & το mapping μένουν σταθερά.
    """

    BASE_URL = "https://api.sofascore.com/api/v1"

    def __init__(self, session: Optional[requests.Session] = None, timeout: float = 10.0):
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_match(self, match_id: str) -> MatchData:
        # Παράδειγμα endpoint – μπορεί να χρειαστεί προσαρμογή
        data = self._get(f"/event/{match_id}")
        event = data["event"]

        home_team = self._map_team(event["homeTeam"])
        away_team = self._map_team(event["awayTeam"])

        kickoff_time = datetime.fromtimestamp(event["startTimestamp"])

        status = self._map_status(event.get("status", {}))

        home_score = event.get("homeScore", {}).get("current")
        away_score = event.get("awayScore", {}).get("current")

        league_name = event.get("tournament", {}).get("name")
        season = event.get("season", {}).get("name")

        return MatchData(
            id=str(event["id"]),
            home_team=home_team,
            away_team=away_team,
            kickoff_time=kickoff_time,
            status=status,
            home_score=home_score,
            away_score=away_score,
            league_name=league_name,
            season=season,
        )

    def get_team(self, team_id: str) -> TeamData:
        data = self._get(f"/team/{team_id}")
        team = data["team"]
        return self._map_team(team)

    def get_player(self, player_id: str) -> PlayerData:
        data = self._get(f"/player/{player_id}")
        player = data["player"]

        team_id = None
        if "team" in player and player["team"] is not None:
            team_id = str(player["team"]["id"])

        return PlayerData(
            id=str(player["id"]),
            name=player["name"],
            position=player.get("position"),
            shirt_number=player.get("shirtNumber"),
            team_id=team_id,
        )

    def get_match_events(self, match_id: str) -> List[EventData]:
        # Παράδειγμα endpoint – μπορεί να χρειαστεί προσαρμογή
        data = self._get(f"/event/{match_id}/incidents")
        incidents = data.get("incidents", [])

        events: List[EventData] = []
        for inc in incidents:
            events.append(
                EventData(
                    id=str(inc.get("id", f"{match_id}-{inc.get('time', {}).get('minute', 0)}-{inc.get('incidentType', 'unknown')}")),
                    match_id=str(match_id),
                    minute=inc.get("time", {}).get("minute", 0),
                    second=inc.get("time", {}).get("second", 0),
                    type=inc.get("incidentType", "unknown"),
                    team_id=str(inc["team"]["id"]) if inc.get("team") else None,
                    player_id=str(inc["player"]["id"]) if inc.get("player") else None,
                    description=inc.get("text"),
                )
            )
        return events

    def get_league_matches(self, league_id: str, season: str) -> List[MatchData]:
        # Εδώ συνήθως χρειάζεται endpoint τύπου tournament/season
        # Θα το αφήσουμε ως placeholder με NotImplementedError για να μην είναι ψευδώς “σωστό”.
        raise NotImplementedError("get_league_matches needs concrete Sofascore endpoint mapping.")

    @staticmethod
    def _map_team(raw: dict) -> TeamData:
        return TeamData(
            id=str(raw["id"]),
            name=raw["name"],
            short_name=raw.get("shortName"),
            country=raw.get("country", {}).get("name") if raw.get("country") else None,
        )

    @staticmethod
    def _map_status(status_raw: dict) -> str:
        # Sofascore έχει διάφορα status codes – εδώ τα χαρτογραφούμε σε 3 βασικά
        type_ = status_raw.get("type")
        if type_ in ("notstarted", "postponed"):
            return "scheduled"
        if type_ in ("inprogress", "live"):
            return "live"
        if type_ in ("finished", "afterextra", "afterpenalties"):
            return "finished"
        return "unknown"
