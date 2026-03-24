import time
from app.services.browser_client import fetch_safely

EVENTS_URL = "https://api.sofascore.com/api/v1/unique-tournament/{tid}/season/{sid}/events"

season_cache = {}
SEASON_CACHE_TTL = 60 * 60 * 12  # 12 hours


def fetch_league_matches(tournament_id: int, season_id: int):
    now = time.time()
    cache_key = f"{tournament_id}_{season_id}"

    # Cache
    if cache_key in season_cache:
        entry = season_cache[cache_key]
        if now - entry["timestamp"] < SEASON_CACHE_TTL:
            print(f"USING CACHED MATCH LIST FOR {cache_key}")
            return entry["data"]

    url = EVENTS_URL.format(tid=tournament_id, sid=season_id)
    print("REQUEST MATCH LIST:", url)

    data = fetch_safely(url)
    if not data:
        print("FAILED TO FETCH MATCH LIST")
        return []

    match_ids = set()

    # 1️⃣ Regular events
    events = data.get("events") or []
    for e in events:
        match_ids.add(e["id"])

    # 2️⃣ Groups (playoff, playout, championship, relegation, etc)
    groups = data.get("groups") or []
    for group in groups:
        group_events = group.get("events") or []
        for e in group_events:
            match_ids.add(e["id"])

    match_ids = list(match_ids)

    # Cache
    season_cache[cache_key] = {
        "timestamp": now,
        "data": match_ids
    }

    return match_ids
