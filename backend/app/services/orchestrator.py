import logging
from app.services.browser_api import BrowserAPI
from app.services.discovery import (
    discover_leagues,
    discover_seasons,
    fetch_season_matches,
)

logger = logging.getLogger(__name__)


def collect_all_world(years_back: int = 10):
    logger.info("🚀 Starting FULL WORLD COLLECTION job...")

    browser = BrowserAPI(headless=True)

    try:
        logger.info("🌍 Starting FULL WORLD DISCOVERY...")
        leagues = discover_leagues(browser)

        logger.info(f"🌍 Total valid leagues discovered: {len(leagues)}")

        for league in leagues:
            ut_id = league["id"]
            name = league["name"]
            country = league["country"]

            logger.info(f"🔍 Discovering seasons for {name} ({country})...")

            seasons = discover_seasons(browser, ut_id, years_back=years_back)

            for season in seasons:
                season_id = season["id"]
                season_name = season["name"]

                logger.info(f"⚽ Fetching matches for {name} - {season_name}...")
                match_ids = fetch_season_matches(browser, ut_id, season_id)

                logger.info(f"📌 Found {len(match_ids)} matches for {name} - {season_name}")

        logger.info("✅ WORLD COLLECTION COMPLETED.")

    finally:
        browser.close()
        logger.info("🏁 Job completed.")
