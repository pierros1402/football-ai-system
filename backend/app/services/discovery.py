import logging
import json
import time
from typing import List, Dict, Any

from app.services.browser_api import BrowserAPI

logger = logging.getLogger(__name__)

BASE_API = "https://api.sofascore.com/api/v1"


# ---------------------------------------------------------
# 55 UEFA COUNTRIES (ISO alpha2 + UK subdivisions + Israel)
# ---------------------------------------------------------
UEFA_COUNTRIES = {
    "AL","AD","AM","AT","AZ","BA","BE","BG","BY","CH","CY","CZ","DE","DK","EE",
    "ES","FI","FO","FR","GE","GI","GR","HR","HU","IE","IS","IT","KZ","LI","LT",
    "LU","LV","MC","MD","ME","MK","MT","NL","NO","PL","PT","RO","RS","RU","SE",
    "SI","SK","SM","TR","UA",
    "GB-ENG","GB-SCT","GB-WLS","GB-NIR",
    "IL"
}


# ---------------------------------------------------------
# FILTER HELPERS
# ---------------------------------------------------------

def is_youth(name: str) -> bool:
    terms = ["u17","u18","u19","u20","u21","u23","youth","academy","juvenil","junior"]
    name = name.lower()
    return any(t in name for t in terms)


def is_regional_cup(name: str) -> bool:
    terms = [
        "regional", "county", "district", "local", "amateur",
        "state cup", "provinc", "depart", "metropolitan",
        "catalunya", "galicia", "andalu", "paulista",
        "federacion", "federation", "liga regional",
        "copa regional", "regional cup"
    ]
    name = name.lower()
    return any(t in name for t in terms)


def is_low_tier(name: str) -> bool:
    terms = [
        "division 3", "division 4", "division 5", "division 6",
        "serie d", "serie e",
        "non league", "amateur league"
    ]
    name = name.lower()
    return any(t in name for t in terms)


def is_top_international(name: str) -> bool:
    terms = [
        "world cup", "euro", "copa america", "africa cup", "asian cup",
        "gold cup", "nations league",
        "champions league", "sudamericana",
        "champions cup", "afc champions", "caf champions", "ofc champions"
    ]
    name = name.lower()
    return any(t in name for t in terms)


# ---------------------------------------------------------
# API HELPERS (Playwright-based)
# ---------------------------------------------------------

def fetch_unique_tournament(browser: BrowserAPI, ut_id: int):
    url = f"{BASE_API}/unique-tournament/{ut_id}"
    logger.info("REQUEST: %s", url)
    return browser.get_json(url)


def fetch_season_events(browser: BrowserAPI, ut_id: int, season_id: int = None):
    if season_id is None:
        ut = fetch_unique_tournament(browser, ut_id)
        season_id = ut["uniqueTournament"]["currentSeason"]["id"]

    url = f"{BASE_API}/unique-tournament/{ut_id}/season/{season_id}/events"
    logger.info("REQUEST: %s", url)
    data = browser.get_json(url)
    return data.get("events", [])


# ---------------------------------------------------------
# DISCOVER ALL LEAGUES (NETWORK INTERCEPT)
# ---------------------------------------------------------

def discover_leagues(browser: BrowserAPI) -> List[Dict[str, Any]]:
    url = f"{BASE_API}/sport/football/categories"
    logger.info("REQUEST: %s", url)

    data = browser.get_json(url)
    categories = data.get("categories", [])
    leagues: List[Dict[str, Any]] = []
    seen_ids = set()

    for cat in categories:
        slug = cat.get("slug")
        alpha2 = cat.get("alpha2", "")
        if not slug:
            continue

        page_url = f"https://www.sofascore.com/football/{slug}"
        logger.info("HTML REQUEST: %s", page_url)

        captured: List[Dict[str, Any]] = []

        def handle_response(response):
            try:
                url = response.url
                if "tournament" not in url:
                    return
                # Μόνο JSON responses
                ct = response.headers.get("content-type", "")
                if "application/json" not in ct:
                    return
                data = response.json()
                captured.append(data)
            except Exception:
                pass

        browser.page.on("response", handle_response)

        try:
            browser.page.goto(page_url, timeout=15000, wait_until="domcontentloaded")
        except Exception:
            logger.warning(f"⚠️ Timeout loading {page_url}, skipping...")
            browser.page.remove_listener("response", handle_response)
            continue

        # Δώσε χρόνο στο React να πυροδοτήσει τα AJAX calls
        time.sleep(2.0)

        browser.page.remove_listener("response", handle_response)

        for resp in captured:
            if not isinstance(resp, dict):
                continue

            # Case 1: response με "tournaments": [...]
            if "tournaments" in resp and isinstance(resp["tournaments"], list):
                for t in resp["tournaments"]:
                    ut = t.get("uniqueTournament", {})
                    ut_id = ut.get("id")
                    ut_name = ut.get("name", "")
                    if not ut_id or not ut_name:
                        continue

                    name_lower = ut_name.lower()

                    if is_youth(name_lower):
                        continue
                    if is_regional_cup(name_lower):
                        continue
                    if not alpha2:
                        if not is_top_international(name_lower):
                            continue
                    if alpha2 not in UEFA_COUNTRIES:
                        if is_low_tier(name_lower):
                            continue

                    if ut_id in seen_ids:
                        continue
                    seen_ids.add(ut_id)

                    leagues.append({
                        "id": ut_id,
                        "name": ut_name,
                        "country": alpha2,
                    })

            # Case 2: response με "uniqueTournament": {...}
            if "uniqueTournament" in resp and isinstance(resp["uniqueTournament"], dict):
                ut = resp["uniqueTournament"]
                ut_id = ut.get("id")
                ut_name = ut.get("name", "")
                if not ut_id or not ut_name:
                    continue

                name_lower = ut_name.lower()

                if is_youth(name_lower):
                    continue
                if is_regional_cup(name_lower):
                    continue
                if not alpha2:
                    if not is_top_international(name_lower):
                        continue
                if alpha2 not in UEFA_COUNTRIES:
                    if is_low_tier(name_lower):
                        continue

                if ut_id in seen_ids:
                    continue
                seen_ids.add(ut_id)

                leagues.append({
                    "id": ut_id,
                    "name": ut_name,
                    "country": alpha2,
                })

    logger.info("🌍 Total valid leagues discovered: %d", len(leagues))
    return leagues


# ---------------------------------------------------------
# DISCOVER SEASONS
# ---------------------------------------------------------

def discover_seasons(browser: BrowserAPI, ut_id: int, years_back: int = 10):
    ut = fetch_unique_tournament(browser, ut_id)
    seasons = ut["uniqueTournament"].get("seasons", [])

    valid_seasons = []
    priority_seasons = []

    for s in seasons:
        season_name = s.get("name", "").lower()
        season_id = s.get("id")

        if is_youth(season_name):
            continue

        if is_regional_cup(season_name):
            continue

        if "25/26" in season_name or "2025" in season_name:
            priority_seasons.append({
                "id": season_id,
                "name": s.get("name"),
                "year": s.get("year"),
            })
            continue

        year_str = s.get("year") or s.get("name")
        if not year_str:
            continue

        digits = "".join(ch for ch in year_str if ch.isdigit())
        if len(digits) >= 4:
            year = int(digits[:4])
        else:
            continue

        if 2015 <= year <= 2025:
            valid_seasons.append({
                "id": season_id,
                "name": s.get("name"),
                "year": s.get("year"),
            })

    return priority_seasons + valid_seasons


# ---------------------------------------------------------
# DISCOVER MATCHES
# ---------------------------------------------------------

def fetch_season_matches(
    browser: BrowserAPI,
    ut_id: int,
    season_id: int,
    include_upcoming: bool = True,
    include_finished: bool = True
) -> List[int]:

    events = fetch_season_events(browser, ut_id, season_id)
    match_ids = []

    for e in events:
        status = e.get("status", {})
        status_type = status.get("type", "").lower()

        name = e.get("tournament", {}).get("name", "")
        if is_youth(name):
            continue

        if is_regional_cup(name):
            continue

        if include_finished and status_type == "finished":
            match_ids.append(e["id"])
            continue

        if include_upcoming and status_type in ["notstarted", "inprogress"]:
            match_ids.append(e["id"])
            continue

        round_info = e.get("roundInfo", {})
        cup_type = round_info.get("cupRoundType")

        if cup_type is not None:
            match_ids.append(e["id"])
            continue

        if "qualification" in round_info.get("slug", "").lower():
            match_ids.append(e["id"])
            continue

        if "playoff" in round_info.get("name", "").lower():
            match_ids.append(e["id"])
            continue

        if "play-out" in round_info.get("name", "").lower():
            match_ids.append(e["id"])
            continue

    return match_ids
