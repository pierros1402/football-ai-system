from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
import json

router = APIRouter(prefix="/stats", tags=["Stats"])

API_BASE = "https://api.sofascore.com/api/v1/event"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

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

    # 3️⃣ Fetch page with browser headers
    page = requests.get(page_url, headers=HEADERS, timeout=10, allow_redirects=True)

    if page.status_code != 200:
        raise HTTPException(status_code=404, detail="Match page not found")

    # 4️⃣ Extract __NEXT_DATA__
    data = extract_next_data(page.text)
    if not data:
        raise HTTPException(status_code=500, detail="Could not extract match data")

    return {
        "match_id": match_id,
        "slug": slug,
        "customId": custom_id,
        "data": data
    }
