import logging
import time
from app.services.browser_client import BrowserClient
from app.services.discovery import discover_leagues, discover_seasons, fetch_season_matches
from app.services.collector import collect_matches

logging.basicConfig(level=logging.INFO)

def update_world():
    logging.info("🔄 Starting incremental update...")

    leagues = discover_leagues()

    with BrowserClient() as client:
        for lg in leagues:
            ut_id = lg["id"]
            league_name = lg["name"]

            seasons = discover_seasons(client, ut_id, years_back=3)

            for s in seasons:
                season_id = s["id"]
                season_name = s["name"]

                match_ids = fetch_season_matches(
                    client,
                    ut_id=ut_id,
                    season_id=season_id,
                    include_upcoming=True,
                    include_finished=False,  # only new/updated
                )

                collect_matches(match_ids, league_name, season_name)

                time.sleep(1)

    logging.info("✅ Incremental update completed.")
