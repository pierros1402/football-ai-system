from fastapi import HTTPException
import time

from app.services.browser_client import BrowserClient
from app.services.normalizer import normalize_full_match

API_BASE = "https://api.sofascore.com/api/v1/event"
STANDINGS_BASE = "https://api.sofascore.com/api/v1/unique-tournament"

# -----------------------------
# Standings Cache
# -----------------------------
standings_cache = {}  # { tournament_id: { "timestamp": ..., "data": ... } }
CACHE_TTL = 60 * 60 * 12  # 12 hours

# -----------------------------
# Form Cache
# -----------------------------
form_cache = {}  # { team_id: { "timestamp": ..., "data": ... } }
FORM_CACHE_TTL = 60 * 60 * 6  # 6 hours


# -----------------------------
# Generic fetch wrapper
# -----------------------------
def _fetch(endpoint: str):
    url = f"{API_BASE}/{endpoint}"
    print("REQUEST:", url)

    try:
        with BrowserClient() as client:
            return client.get_json(url)
    except Exception:
        print("FAILED FETCH:", url)
        return None


# -----------------------------
# Standings fetcher with caching
# -----------------------------
def fetch_standings(tournament_id: int):
    now = time.time()

    if tournament_id in standings_cache:
        entry = standings_cache[tournament_id]
        if now - entry["timestamp"] < CACHE_TTL:
            print(f"USING CACHED STANDINGS FOR TOURNAMENT {tournament_id}")
            return entry["data"]

    url = f"{STANDINGS_BASE}/{tournament_id}/standings/total"
    print("REQUEST STANDINGS:", url)

    try:
        with BrowserClient() as client:
            data = client.get_json(url)
    except Exception:
        print("FAILED TO FETCH STANDINGS")
        return None

    standings_cache[tournament_id] = {
        "timestamp": now,
        "data": data
    }

    return data


# -----------------------------
# Form fetcher with caching
# -----------------------------
def fetch_form(team_id: int, count: int = 10):
    now = time.time()

    if team_id in form_cache:
        entry = form_cache[team_id]
        if now - entry["timestamp"] < FORM_CACHE_TTL:
            print(f"USING CACHED FORM FOR {team_id}")
            return entry["data"]

    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/{count}"
    print("REQUEST FORM:", url)

    try:
        with BrowserClient() as client:
            data = client.get_json(url)
    except Exception:
        print("FAILED TO FETCH FORM")
        return None

    form_cache[team_id] = {
        "timestamp": now,
        "data": data
    }

    return data


# -----------------------------
# FULL MATCH DATA SERVICE
# -----------------------------
def get_full_match_data(match_id: int) -> dict:
    event = _fetch(f"{match_id}")
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = event.get("event")
    if not event_data:
        raise HTTPException(status_code=404, detail="Invalid event data")

    # Tournament ID fallback logic
    tournament_id = (
        event_data.get("uniqueTournament", {}).get("id")
        or event_data.get("tournament", {}).get("uniqueTournament", {}).get("id")
        or event_data.get("tournament", {}).get("id")
    )

    standings = fetch_standings(tournament_id)

    home_team_id = event_data["homeTeam"]["id"]
    away_team_id = event_data["awayTeam"]["id"]

    home_form = fetch_form(home_team_id, 10)
    away_form = fetch_form(away_team_id, 10)

    timeline = _fetch(f"{match_id}/timeline")
    incidents = _fetch(f"{match_id}/incidents")
    statistics = _fetch(f"{match_id}/statistics")
    lineups = _fetch(f"{match_id}/lineups")
    momentum = _fetch(f"{match_id}/momentum")
    graph = _fetch(f"{match_id}/graph")

    return {
        "match_id": match_id,
        "event": event_data,
        "standings": standings.get("standings") if standings else None,
        "form": {
            "home": home_form.get("events") if home_form else None,
            "away": away_form.get("events") if away_form else None,
        },
        "timeline": timeline.get("timeline") if timeline else None,
        "incidents": incidents.get("incidents") if incidents else None,
        "statistics": statistics.get("statistics") if statistics else None,
        "lineups": lineups.get("lineups") if lineups else None,
        "momentum": momentum.get("momentum") if momentum else None,
        "graph": graph.get("graphPoints") if graph else None,
    }


# -----------------------------
# NORMALIZED MATCH DATA SERVICE
# -----------------------------
def get_normalized_match(match_id: int) -> dict:
    full = get_full_match_data(match_id)
    normalized = normalize_full_match(full)
    return normalized
