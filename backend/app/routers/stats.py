from fastapi import APIRouter, HTTPException
from app.services.browser_client import fetch_safely
import time

router = APIRouter(prefix="/stats", tags=["Stats"])

API_BASE = "https://api.sofascore.com/api/v1/event"
STANDINGS_BASE = "https://api.sofascore.com/api/v1/unique-tournament"

# -----------------------------
# Simple in-memory cache
# -----------------------------
standings_cache = {}  # { tournament_id: { "timestamp": ..., "data": ... } }
CACHE_TTL = 60 * 60 * 12  # 12 hours


# -----------------------------
# Generic fetch wrapper
# -----------------------------
def fetch(endpoint: str):
    url = f"{API_BASE}/{endpoint}"
    print("REQUEST:", url)
    data = fetch_safely(url)
    if data is None:
        print("FAILED FETCH:", url)
    return data


# -----------------------------
# Standings fetcher with caching
# -----------------------------
def fetch_standings(tournament_id: int):
    now = time.time()

    # Return cached standings if fresh
    if tournament_id in standings_cache:
        entry = standings_cache[tournament_id]
        if now - entry["timestamp"] < CACHE_TTL:
            print(f"USING CACHED STANDINGS FOR TOURNAMENT {tournament_id}")
            return entry["data"]

    # Fetch fresh standings
    url = f"{STANDINGS_BASE}/{tournament_id}/standings/total"
    print("REQUEST STANDINGS:", url)
    data = fetch_safely(url)

    if data is None:
        print("FAILED TO FETCH STANDINGS")
        return None

    standings_cache[tournament_id] = {
        "timestamp": now,
        "data": data
    }

    return data


# -----------------------------
# FULL MATCH DATA ENDPOINT
# -----------------------------
@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):

    # 1️⃣ Event info
    event = fetch(f"{match_id}")
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = event.get("event")
    if not event_data:
        raise HTTPException(status_code=404, detail="Invalid event data")

    # Extract tournament ID for standings
    tournament_id = event_data["uniqueTournament"]["id"]

    # 2️⃣ Standings
    standings = fetch_standings(tournament_id)

    # 3️⃣ Timeline
    timeline = fetch(f"{match_id}/timeline")

    # 4️⃣ Incidents
    incidents = fetch(f"{match_id}/incidents")

    # 5️⃣ Statistics
    statistics = fetch(f"{match_id}/statistics")

    # 6️⃣ Lineups
    lineups = fetch(f"{match_id}/lineups")

    # 7️⃣ Momentum
    momentum = fetch(f"{match_id}/momentum")

    # 8️⃣ Graph (win probability)
    graph = fetch(f"{match_id}/graph")

    # 🔁 Merge everything
    return {
        "match_id": match_id,
        "event": event_data,
        "standings": standings.get("standings") if standings else None,
        "timeline": timeline.get("timeline") if timeline else None,
        "incidents": incidents.get("incidents") if incidents else None,
        "statistics": statistics.get("statistics") if statistics else None,
        "lineups": lineups.get("lineups") if lineups else None,
        "momentum": momentum.get("momentum") if momentum else None,
        "graph": graph.get("graphPoints") if graph else None,
    }
