import logging
import time
import random

from app.services.browser_client import BrowserClient
from app.services.discovery import (
    discover_leagues,
    discover_seasons,
    fetch_season_matches,
)
from app.services.collector import collect_matches

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# MAIN ORCHESTRATOR
# ---------------------------------------------------------

def collect_all_world(years_back: int = 10):
    """
    Full world data collection:
    - Discover all leagues (with filtering)
    - Discover seasons (priority 25–26 + 10 years back)
    - Fetch matches (finished + upcoming + playoffs)
    - Normalize & store
    """

    logger.info("🌍 Starting FULL WORLD DISCOVERY...")

    leagues = discover_leagues()
    logger.info(f"🌍 Total valid leagues discovered: {len(leagues)}")

    with BrowserClient() as client:
        for lg in leagues:
            ut_id = lg["id"]
            league_name = lg["name"]
            country = lg["country"]

            logger.info(f"\n🏆 LEAGUE: {league_name} ({country})")

            # ---- Discover seasons ----
            seasons = discover_seasons(client, ut_id, years_back=years_back)
            logger.info(f"  → Seasons found: {len(seasons)}")

            for s in seasons:
                season_id = s["id"]
                season_name = s["name"]

                logger.info(f"    📅 Season: {season_name}")

                # ---- Fetch matches ----
                match_ids = fetch_season_matches(
                    client,
                    ut_id=ut_id,
                    season_id=season_id,
                    include_upcoming=True,
                    include_finished=True,
                )

                logger.info(f"      → Matches: {len(match_ids)}")

                # ---- Collect matches ----
                collect_matches(match_ids, league_name, season_name)

                # ---- Anti-bot throttling ----
                time.sleep(random.uniform(0.8, 1.6))

    logger.info("✅ WORLD COLLECTION COMPLETED.")


# ---------------------------------------------------------
# RUN SPECIFIC LEAGUE
# ---------------------------------------------------------

def collect_single_league(ut_id: int, years_back: int = 10):
    """
    Collects all seasons + matches for a single league.
    """

    with BrowserClient() as client:
        ut = client.get_json(f"https://api.sofascore.com/api/v1/unique-tournament/{ut_id}")
        league_name = ut["uniqueTournament"]["name"]

        logger.info(f"🏆 SINGLE LEAGUE: {league_name}")

        seasons = discover_seasons(client, ut_id, years_back=years_back)

        for s in seasons:
            season_id = s["id"]
            season_name = s["name"]

            logger.info(f"  📅 Season: {season_name}")

            match_ids = fetch_season_matches(
                client,
                ut_id=ut_id,
                season_id=season_id,
                include_upcoming=True,
                include_finished=True,
            )

            logger.info(f"    → Matches: {len(match_ids)}")

            collect_matches(match_ids, league_name, season_name)

            time.sleep(random.uniform(0.8, 1.6))
