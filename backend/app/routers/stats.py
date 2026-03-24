from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/stats", tags=["Stats"])

BASE = "https://api.sofascore.com/api/v1/event"

ENDPOINTS = {
    "summary": "",
    "timeline": "timeline",
    "incidents": "incidents",
    "statistics": "statistics",
    "lineups": "lineups",
    "momentum": "momentum",
    "graph": "graph"
}

def fetch(url: str):
    """Helper to fetch Sofascore data safely."""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):
    result = {}

    for key, endpoint in ENDPOINTS.items():
        url = f"{BASE}/{match_id}/{endpoint}" if endpoint else f"{BASE}/{match_id}"
        data = fetch(url)
        result[key] = data  # μπορεί να είναι None, και αυτό είναι ΟΚ

    # Αν ΟΛΑ είναι None → το match δεν υπάρχει
    if all(v is None for v in result.values()):
        raise HTTPException(status_code=404, detail="Match not found")

    return {
        "match_id": match_id,
        "data": result
    }
