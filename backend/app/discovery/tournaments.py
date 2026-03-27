from sqlalchemy import select
from app.models.tournament import Tournament
from app.services.browser_client import BrowserClient


class TournamentDiscovery:
    MOBILE_URL = "https://api.sofascore.com/mobile/v4/unique-tournaments"

    def __init__(self, db):
        self.db = db

    async def fetch_tournaments_from_api(self):
        with BrowserClient() as browser:
            return browser.get_json(self.MOBILE_URL)

    async def sync(self):
        raw = await self.fetch_tournaments_from_api()
        tournaments = raw.get("uniqueTournaments", [])

        for t in tournaments:
            await self._upsert_tournament(t)

        await self.db.commit()

    async def _upsert_tournament(self, t):
        stmt = select(Tournament).where(Tournament.id == t["id"])
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        country = t.get("country", {}).get("name")

        if existing:
            changed = False

            if existing.name != t.get("name"):
                existing.name = t.get("name")
                changed = True

            if existing.slug != t.get("slug"):
                existing.slug = t.get("slug")
                changed = True

            if existing.country != country:
                existing.country = country
                changed = True

            if existing.priority != t.get("priority"):
                existing.priority = t.get("priority")
                changed = True

            if changed:
                existing.json_data = t

            return

        new_t = Tournament(
            id=t["id"],
            name=t.get("name"),
            slug=t.get("slug"),
            country=country,
            priority=t.get("priority"),
            json_data=t,
        )

        self.db.add(new_t)
