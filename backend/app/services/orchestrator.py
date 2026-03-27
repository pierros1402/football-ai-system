import logging
from app.services.browser_api import BrowserAPI
from app.services.discover_countries_ssr import discover_all_countries
from app.services.discovery import (
    discover_tournaments_from_country,
    discover_seasons,
    discover_matches,
)
from app.services.storage import (
    save_country,
    save_tournament,
    save_season,
    save_match,
)

logger = logging.getLogger(__name__)


def collect_all_world():
    logger.info("🚀 Starting FULL WORLD COLLECTION job (SSR + PostgreSQL)...")

    browser = BrowserAPI(headless=True)

    try:
        countries = discover_all_countries(browser)
        logger.info(f"🌍 Total countries: {len(countries)}")

        for country in countries:
            cid = country["id"]
            cname = country["name"]
            cslug = country["slug"]

            save_country(cid, cname, cslug)

            tournaments = discover_tournaments_from_country(browser, cslug)

            for t in tournaments:
                ut_id = t["id"]
                ut_name = t["name"]
                ut_slug = t["slug"]

                save_tournament(ut_id, ut_name, ut_slug, cid)

                seasons = discover_seasons(browser, ut_slug, ut_id)

                for s in seasons:
                    season_id = s["id"]
                    season_name = s["name"]

                    save_season(season_id, season_name, ut_id)

                    matches = discover_matches(browser, ut_slug, ut_id, season_id)

                    for m in matches:
                        match_id = m["id"]
                        save_match(match_id, ut_id, season_id, m)

        logger.info("✅ WORLD COLLECTION COMPLETED.")

    finally:
        browser.close()
