from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/stats", tags=["Stats"])

API_BASE = "https://api.sofascore.com/api/v1/event"

def fetch(endpoint: str):
    url = f"{API_BASE}/{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/",
    }
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        print("FAILED:", r.status_code, r.text[:200])
        return None
    return r.json()


@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):
    print("URL:", f"{API_BASE}/{match_id}")

    # 1️⃣ Event info
    event = fetch(f"{match_id}")
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2️⃣ Timeline
    timeline = fetch(f"{match_id}/timeline")

    # 3️⃣ Incidents
    incidents = fetch(f"{match_id}/incidents")

    # 4️⃣ Statistics
    statistics = fetch(f"{match_id}/statistics")

    # 5️⃣ Lineups
    lineups = fetch(f"{match_id}/lineups")

    # 6️⃣ Momentum
    momentum = fetch(f"{match_id}/momentum")

    # 7️⃣ Graph (win probability)
    graph = fetch(f"{match_id}/graph")

    # 8️⃣ Merge everything
    return {
        "match_id": match_id,
        "event": event.get("event"),
        "timeline": timeline.get("timeline") if timeline else None,
        "incidents": incidents.get("incidents") if incidents else None,
        "statistics": statistics.get("statistics") if statistics else None,
        "lineups": lineups.get("lineups") if lineups else None,
        "momentum": momentum.get("momentum") if momentum else None,
        "graph": graph.get("graphPoints") if graph else None,
    }
