from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/stats", tags=["Stats"])

API_BASE = "https://api.sofascore.com/api/v1/event"

def fetch(endpoint: str):
    url = f"{API_BASE}/{endpoint}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()

@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):

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
