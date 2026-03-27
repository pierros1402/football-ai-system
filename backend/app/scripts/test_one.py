import logging
from app.services.browser_api import BrowserAPI
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    browser = BrowserAPI(headless=True)

    try:
        # 1) Test country
        country_slug = "england"
        country_id = 1
        country_name = "England"

        print("Saving country...")
        save_country(country_id, country_name, country_slug)

        # 2) Discover tournaments
        print("Discovering tournaments...")
        tournaments = discover_tournaments_from_country(browser, country_slug)
        print(f"Found {len(tournaments)} tournaments in England")

        t = tournaments[0]
        ut_id = t["id"]
        ut_slug = t["slug"]
        ut_name = t["name"]

        print("Saving tournament...")
        save_tournament(ut_id, ut_name, ut_slug, country_id)

        # 3) Discover seasons
        print("Discovering seasons...")
        seasons = discover_seasons(browser, ut_slug, ut_id)
        print(f"Found {len(seasons)} seasons")

        s = seasons[0]
        season_id = s["id"]
        season_name = s["name"]

        print("Saving season...")
        save_season(season_id, season_name, ut_id)

        # 4) Discover matches
        print("Discovering matches...")
        matches = discover_matches(browser, ut_slug, ut_id, season_id)
        print(f"Found {len(matches)} matches")

        if matches:
            m = matches[0]
            match_id = m["id"]

            print("Saving match...")
            save_match(match_id, ut_id, season_id, m)

        print("\n✅ TEST COMPLETED SUCCESSFULLY")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
