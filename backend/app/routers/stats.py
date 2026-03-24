from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
import json

router = APIRouter(prefix="/stats", tags=["Stats"])

API_BASE = "https://api.sofascore.com/api/v1/event"

def extract_next_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script_tag:
        return None
    return json.loads(script_tag.string)

@router.get("/full/{match_id}")
def get_full_match_data(match_id: int):

    # 1️⃣ Get slug + customId from Sofascore API
    api_url = f"{API_BASE}/{match_id}"
    r = requests.get(api_url, timeout=10)

    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="Match not found in API")

    event = r.json().get("event")
    if not event:
        raise HTTPException(status_code=404, detail="Invalid event data")

    slug = event.get("slug")
    custom_id = event.get("customId")

    if not slug or not custom_id:
        raise HTTPException(status_code=500, detail="Missing slug or customId")

    # 2️⃣ Build correct Sofascore page URL
    page_url = f"https://www.sofascore.com/el/football/match/{slug}/{custom_id}"

    page = requests.get(page_url, timeout=10)
    if page.status_code != 200:
        raise HTTPException(status_code=404, detail="Match page not found")

    # 3️⃣ Extract __NEXT_DATA__
    data = extract_next_data(page.text)
    if not data:
        raise HTTPException(status_code=500, detail="Could not extract match data")

    return {
        "match_id": match_id,
        "slug": slug,
        "customId": custom_id,
        "data": data
    }
