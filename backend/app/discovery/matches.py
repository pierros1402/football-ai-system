from sqlalchemy import select
from app.models.match import Match
from app.services.browser_client import BrowserClient


class MatchDiscovery:
    MOBILE_URL = "https://api.sofascore.com/mobile/v4/unique-tournaments/{tournament_id}/seasons/{season_id}/events"

    def __init__(self, db):
        self.db = db

    async def fetch_matches(self, tournament_id: int, season_id: int):
        url = self.MOBILE_URL.format(tournament_id=tournament_id, season_id=season_id)
        with BrowserClient() as browser:
            return browser.get_json(url)

    async def sync(self, tournament_id: int, season_id: int):
        raw = await self.fetch_matches(tournament_id, season_id)
        matches = raw.get("events", [])

        for m in matches:
            await self._upsert_match(m, tournament_id, season_id)

        await self.db.commit()

    async def _upsert_match(self, m, tournament_id, season_id):
        stmt = select(Match).where(Match.id == m["id"])
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.json_data = m
            return

        new_m = Match(
            id=m["id"],
            tournament_id=tournament_id,
            season_id=season_id,
            start_timestamp=m.get("startTimestamp"),
            status=m.get("status", {}).get("type"),
            round=m.get("roundInfo", {}).get("round"),
            venue=m.get("venue", {}).get("stadium", {}).get("name"),
            home_team_id=m.get("homeTeam", {}).get("id"),
            away_team_id=m.get("awayTeam", {}).get("id"),
            score_home=m.get("homeScore", {}).get("current"),
            score_away=m.get("awayScore", {}).get("current"),
            json_data=m,
        )

        self.db.add(new_m)
