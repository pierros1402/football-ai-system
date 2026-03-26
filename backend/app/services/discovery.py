import logging
from typing import List, Dict, Any

from app.services.browser_api import BrowserAPI
from app.services.ssr_discovery import fetch_next_data
from app.services.ssr_parser import (
    parse_tournament,
    parse_seasons,
    parse_matches
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# DISCOVER TOURNAMENTS FROM COUNTRY PAGE (SSR)
# ---------------------------------------------------------

def discover_tournaments_from_country(browser: BrowserAPI, country_slug: str) -> List[Dict[str, Any]]:
    """
    Παίρνει ΟΛΑ τα tournaments από τη σελίδα της χώρας:
    https://www.sofascore.com/el/football/<country_slug>
    """

    url = f"https://www.sofascore.com/el/football/{country_slug}"
    logger.info(f"🌍 Fetching tournaments for country: {country_slug}")

    data = fetch_next_data(browser, url)
    if not data:
        logger.warning("⚠️ No __NEXT_DATA__ for country page")
        return []

    page_props = data["props"]["pageProps"]

    # Τα tournaments βρίσκονται εδώ:
    # pageProps["initialState"]["category"]["uniqueTournaments"]
    tournaments = (
        page_props.get("initialState", {})
        .get("category", {})
        .get("uniqueTournaments", [])
    )

    logger.info(f"📌 Found {len(tournaments)} tournaments in {country_slug}")
    return tournaments


# ---------------------------------------------------------
# DISCOVER SEASONS FROM TOURNAMENT PAGE (SSR)
# ---------------------------------------------------------

def discover_seasons(browser: BrowserAPI, tournament_slug: str, tournament_id: int) -> List[Dict[str, Any]]:
    """
    Παίρνει seasons από τη σελίδα του tournament:
    https://www.sofascore.com/el/football/tournament/<country>/<slug>/<id>
    """

    url = f"https://www.sofascore.com/el/football/tournament/{tournament_slug}/{tournament_id}"
    logger.info(f"📅 Fetching seasons for tournament {tournament_slug} ({tournament_id})")

    data = fetch_next_data(browser, url)
    if not data:
        return []

    page_props = data["props"]["pageProps"]
    seasons = parse_seasons(page_props)

    logger.info(f"📌 Found {len(seasons)} seasons")
    return seasons


# ---------------------------------------------------------
# DISCOVER MATCHES FROM SEASON PAGE (SSR)
# ---------------------------------------------------------

def discover_matches(browser: BrowserAPI, tournament_slug: str, tournament_id: int, season_id: int) -> List[Dict[str, Any]]:
    """
    Παίρνει matches από τη σελίδα της season:
    https://www.sofascore.com/el/football/tournament/<country>/<slug>/<id>/season/<season_id>
    """

    url = f"https://www.sofascore.com/el/football/tournament/{tournament_slug}/{tournament_id}/season/{season_id}"
    logger.info(f"⚽ Fetching matches for season {season_id}")

    data = fetch_next_data(browser, url)
    if not data:
        return []

    page_props = data["props"]["pageProps"]
    matches = parse_matches(page_props)

    logger.info(f"📌 Found {len(matches)} matches")
    return matches
