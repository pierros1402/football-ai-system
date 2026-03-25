import logging
from typing import Any, Dict, List, Optional

from app.services.browser_client import BrowserClient

logger = logging.getLogger(__name__)

BASE_API = "https://api.sofascore.com/api/v1"


class LeagueFetcher:
    def __init__(self, client: BrowserClient):
        self.client = client
        self._form_cache = {}

    def _fetch(self, url: str):
        logger.info("REQUEST: %s", url)
        try:
            return self.client.get_json(url)
        except Exception:
            logger.warning("FAILED FETCH: %s", url)
            return None

    def build_league_snapshot(self, match_id: int) -> Dict[str, Any]:
        event_url = f"{BASE_API}/event/{match_id}"
        event_data = self._fetch(event_url)
        if not event_data:
            return {}

        event = event_data["event"]

        home_id = event["homeTeam"]["id"]
        away_id = event["awayTeam"]["id"]

        form_home = self._fetch(f"{BASE_API}/team/{home_id}/events/last/10")
        form_away = self._fetch(f"{BASE_API}/team/{away_id}/events/last/10")

        ut_id = event["tournament"]["uniqueTournament"]["id"]
        standings = self._fetch(f"{BASE_API}/unique-tournament/{ut_id}/standings/total")

        return {
            "match_id": match_id,
            "league": {
                "id": None,
                "name": None,
                "country": None,
                "season_id": event["season"]["id"],
                "season_name": event["season"]["name"],
            },
            "teams": {
                "home": event["homeTeam"],
                "away": event["awayTeam"],
            },
            "result": {
                "home_goals": event["homeScore"].get("current"),
                "away_goals": event["awayScore"].get("current"),
                "winner": "home" if event.get("winnerCode") == 1 else "away" if event.get("winnerCode") == 2 else None,
                "status": event["status"]["description"],
            },
            "standings_snapshot": {
                "table": standings.get("standings") if standings else [],
                "home_row": None,
                "away_row": None,
            },
            "form": {
                "home_last_10": form_home.get("events") if form_home else [],
                "away_last_10": form_away.get("events") if form_away else [],
            },
        }
