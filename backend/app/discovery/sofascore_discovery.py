import logging
import json
import os
import time
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.browser_client import BrowserClient

logger = logging.getLogger(__name__)

BASE_URL = "https://api.sofascore.com/api/v1"
CACHE_FILE = "sofascore_cache.json"

# ------------------------------------------
# SIMPLE FILE CACHE
# ------------------------------------------

_cache: Dict[str, Dict[str, Any]] = {}
_cache_loaded = False


def _load_cache() -> None:
    global _cache_loaded, _cache
    if _cache_loaded:
        return
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}
    else:
        _cache = {}
    _cache_loaded = True


def _save_cache() -> None:
    if not _cache_loaded:
        return
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f)
    except Exception as e:
        logger.error(f"❌ Error saving cache: {e}")


def cached_get_json(client: BrowserClient, path: str, max_age_seconds: int) -> Dict[str, Any]:
    _load_cache()
    url = f"{BASE_URL}/{path.lstrip('/')}"
    now = int(time.time())

    entry = _cache.get(url)
    if entry:
        ts = entry.get("ts", 0)
        if now - ts <= max_age_seconds:
            logger.info(f"🗂  Cache HIT for {url}")
            return entry["data"]

    logger.info(f"🌐 Cache MISS for {url}")
    data = client.get_json(url)
    _cache[url] = {"ts": now, "data": data}
    _save_cache()
    return data


def browser_get_json(client: BrowserClient, path: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    return client.get_json(url)


# ------------------------------------------
# STEP 1 — GET LIVE EVENTS (NO CACHE)
# ------------------------------------------

def discover_live_events(client: BrowserClient) -> List[Dict[str, Any]]:
    logger.info("🔍 Fetching LIVE events from Sofascore...")

    data = browser_get_json(client, "sport/football/events/live")
    events = data.get("events", [])

    logger.info(f"⚽ Live events discovered: {len(events)}")
    return events


# ------------------------------------------
# STEP 2 — EXTRACT UNIQUE TOURNAMENTS
# ------------------------------------------

def extract_unique_tournaments(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logger.info("🏆 Extracting tournaments from live events...")

    tournaments = {}
    for e in events:
        t = e.get("tournament", {})
        ut = t.get("uniqueTournament", {})
        ut_id = ut.get("id")

        if not ut_id:
            continue

        tournaments[ut_id] = {
            "name": ut.get("name"),
            "uniqueTournament": {"id": ut_id},
        }

    logger.info(f"🏆 Unique tournaments found: {len(tournaments)}")
    return list(tournaments.values())


# ------------------------------------------
# STEP 3 — GET SEASONS FOR EACH TOURNAMENT (CACHED)
# ------------------------------------------

def discover_seasons(client: BrowserClient, tournament: Dict[str, Any]) -> List[Dict[str, Any]]:
    ut_id = tournament["uniqueTournament"]["id"]
    logger.info(f"➡️  Seasons for tournament: {tournament['name']} (UT {ut_id})")

    data = cached_get_json(client, f"unique-tournament/{ut_id}/seasons", max_age_seconds=24 * 3600)
    seasons = data.get("seasons", [])

    logger.info(f"   • Seasons found: {len(seasons)}")

    return seasons[:6]  # last 6 seasons


# ------------------------------------------
# STEP 4 — GET MATCHES FOR EACH SEASON (CACHED + 404 SAFE)
# ------------------------------------------

def discover_matches(client: BrowserClient, tournament: Dict[str, Any], season: Dict[str, Any]) -> List[int]:
    ut_id = tournament["uniqueTournament"]["id"]
    sid = season["id"]

    logger.info(f"      ➡️  Matches for {tournament['name']} – Season {season.get('year', sid)}")

    path = f"unique-tournament/{ut_id}/season/{sid}/events"

    try:
        data = cached_get_json(client, path, max_age_seconds=3600)
    except RuntimeError as e:
        if "404" in str(e):
            logger.info(f"         • No events (404) → skipping season")
            return []
        raise

    events = data.get("events", [])
    logger.info(f"         • Matches found: {len(events)}")

    return [e["id"] for e in events if "id" in e]


# ------------------------------------------
# FULL DISCOVERY PIPELINE (PARALLEL + CACHE)
# ------------------------------------------

def get_all_relevant_match_ids_sync() -> List[int]:
    logger.info("🚀 Starting Sofascore discovery pipeline (PARALLEL + CACHE)...")

    all_ids: List[int] = []

    with BrowserClient() as client:
        live_events = discover_live_events(client)
        tournaments = extract_unique_tournaments(live_events)

        # PARALLEL SEASONS
        logger.info("⚡ Fetching seasons in parallel...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            season_futures = {
                executor.submit(discover_seasons, client, t): t
                for t in tournaments
            }

            tournament_seasons = {}
            for future in as_completed(season_futures):
                t = season_futures[future]
                try:
                    tournament_seasons[t["uniqueTournament"]["id"]] = future.result()
                except Exception as e:
                    logger.error(f"❌ Error fetching seasons for {t['name']}: {e}")
                    tournament_seasons[t["uniqueTournament"]["id"]] = []

        # PARALLEL MATCHES
        logger.info("⚡ Fetching matches in parallel...")

        with ThreadPoolExecutor(max_workers=20) as executor:
            match_futures = {}

            for t in tournaments:
                ut_id = t["uniqueTournament"]["id"]
                seasons = tournament_seasons.get(ut_id, [])

                for s in seasons:
                    match_futures[
                        executor.submit(discover_matches, client, t, s)
                    ] = (t, s)

            for future in as_completed(match_futures):
                t, s = match_futures[future]
                try:
                    ids = future.result()
                    all_ids.extend(ids)
                except Exception as e:
                    logger.error(
                        f"❌ Error fetching matches for {t['name']} season {s.get('year')}: {e}"
                    )

    unique_ids = sorted(set(all_ids))
    logger.info(f"✅ Discovery complete. Total matches collected: {len(unique_ids)}")

    return unique_ids
