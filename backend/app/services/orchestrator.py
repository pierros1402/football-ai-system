import logging
from app.services.browser_api import BrowserAPI
from app.services.discover_countries_ssr import discover_all_countries
from app.services.discovery import (
    discover_tournaments_from_country,
    discover_seasons,
    discover_matches,
)

logger = logging.getLogger(__name__)


def collect_all_world():
    logger.info("🚀 Starting FULL WORLD COLLECTION job (SSR mode)...")

    browser = BrowserAPI(headless=True)

    try:
        # 1) ΟΛΕΣ οι χώρες
        countries = discover_all_countries(browser)
        logger.info(f"🌍 Total countries: {len(countries)}")

        for country in countries:
            country_slug = country.get("slug")
            country_name = country.get("name")

            if not country_slug:
                continue

            logger.info(f"\n🌍 COUNTRY: {country_name} ({country_slug})")

            # 2) ΟΛΑ τα tournaments της χώρας
            tournaments = discover_tournaments_from_country(browser, country_slug)
            logger.info(f"📌 Found {len(tournaments)} tournaments in {country_name}")

            for t in tournaments:
                ut_id = t.get("id")
                ut_slug = t.get("slug")
                ut_name = t.get("name")

                if not ut_id or not ut_slug:
                    continue

                logger.info(f"\n🏆 TOURNAMENT: {ut_name} ({ut_id})")

                # 3) ΟΛΕΣ οι seasons
                seasons = discover_seasons(browser, ut_slug, ut_id)
                logger.info(f"📅 Seasons found: {len(seasons)}")

                for s in seasons:
                    season_id = s.get("id")
                    season_name = s.get("name")

                    if not season_id:
                        continue

                    logger.info(f"⚽ SEASON: {season_name} ({season_id})")

                    # 4) ΟΛΑ τα matches
                    matches = discover_matches(browser, ut_slug, ut_id, season_id)
                    logger.info(f"📌 Matches found: {len(matches)}")

        logger.info("\n✅ WORLD COLLECTION COMPLETED (SSR).")

    finally:
        browser.close()
        logger.info("🏁 Job completed.")
