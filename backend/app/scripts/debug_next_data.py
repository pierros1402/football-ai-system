import sys
import os
import logging
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.services.browser_api import BrowserAPI
from app.services.ssr_discovery import fetch_next_data
from app.services.ssr_parser import parse_tournament, parse_seasons, parse_matches

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

URL = "https://www.sofascore.com/el/football/tournament/england/premier-league/17"


if __name__ == "__main__":
    browser = BrowserAPI(headless=True)

    try:
        data = fetch_next_data(browser, URL)
        page_props = data["props"]["pageProps"]

        tournament = parse_tournament(page_props)
        seasons = parse_seasons(page_props)
        matches = parse_matches(page_props)

        print("\n=== TOURNAMENT ===")
        print(json.dumps(tournament, indent=2, ensure_ascii=False))

        print("\n=== SEASONS ===")
        print(json.dumps(seasons[:5], indent=2, ensure_ascii=False))

        print("\n=== MATCHES ===")
        print(json.dumps(matches[:5], indent=2, ensure_ascii=False))

    finally:
        browser.close()
