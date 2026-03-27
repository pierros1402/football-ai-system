import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session

from app.discovery.tournaments import TournamentDiscovery
from app.discovery.seasons import SeasonDiscovery
from app.discovery.matches import MatchDiscovery


async def run_discovery():
    async with async_session() as db:  # type: AsyncSession

        tournaments = TournamentDiscovery(db)
        seasons = SeasonDiscovery(db)
        matches = MatchDiscovery(db)

        print("🔵 Syncing tournaments...")
        await tournaments.sync()

        print("🟡 Syncing seasons...")
        await seasons.sync()

        print("🔴 Syncing matches...")
        await matches.sync()

    print("✅ Discovery pipeline completed.")


if __name__ == "__main__":
    asyncio.run(run_discovery())
