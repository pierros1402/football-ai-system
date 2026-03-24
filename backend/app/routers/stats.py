from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/stats", tags=["Stats"])

BASE = "https://api.sofascore.com/api/v1/event"

def fetch(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):
    summary = fetch(f"{BASE}/{match_id}")

    if summary is None:
        raise HTTPException(status_code=404, detail="Match not found")

    timeline = fetch(f"{BASE}/{match_id}/timeline")
    incidents = fetch(f"{BASE}/{match_id}/incidents")

    # advanced endpoints (may return None)
    statistics = fetch(f"{BASE}/{match_id}/statistics")
    momentum = fetch(f"{BASE}/{match_id}/momentum")
    graph = fetch(f"{BASE}/{match_id}/graph")
    lineups = fetch(f"{BASE}/{match_id}/lineups")

    return {
        "match_id": match_id,
        "summary": summary,
        "timeline": timeline,
        "incidents": incidents,
        "statistics": statistics,
        "momentum": momentum,
        "graph": graph,
        "lineups": lineups
    }
