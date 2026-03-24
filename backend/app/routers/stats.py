from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
import json

router = APIRouter(prefix="/stats", tags=["Stats"])

def extract_next_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script_tag:
        return None
    try:
        return json.loads(script_tag.string)
    except:
        return None

@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):
    url = f"https://www.sofascore.com/el/football/match/{match_id}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="Match page not found")

    data = extract_next_data(r.text)

    if not data:
        raise HTTPException(status_code=500, detail="Could not extract match data")

    return {
        "match_id": match_id,
        "data": data
    }
