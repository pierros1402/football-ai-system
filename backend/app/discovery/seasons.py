from sqlalchemy import select
from app.models.season import Season
from app.services.browser_client import BrowserClient


class SeasonDiscovery:
    MOBILE_URL = "https://api.sofascore.com/mobile/v4/unique-tournaments/{tournament_id}/seasons"

    def __init__(self, db):
        self.db = db

    async def fetch_seasons(self, tournament_id: int):
        url = self.MOBILE_URL.format(tournament_id=tournament_id)
        with BrowserClient() as browser:
            return browser.get_json(url)

    async def sync(self, tournament_id: int):
        raw = await self.fetch_seasons(tournament_id)
        seasons = raw.get("seasons", [])

        for s in seasons:
            await self._upsert_season(s, tournament_id)

        await self.db.commit()

    async def _upsert_season(self, s, tournament_id):
        stmt = select(Season).where(Season.id == s["id"])
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            changed = False

            if existing.name != s.get("name"):
                existing.name = s.get("name")
                changed = True

            if existing.year != s.get("year"):
                existing.year = s.get("year")
                changed = True

            if changed:
                existing.json_data = s

            return

        new_s = Season(
            id=s["id"],
            tournament_id=tournament_id,
            name=s.get("name"),
            year=s.get("year"),
            json_data=s,
        )

        self.db.add(new_s)
