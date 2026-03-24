import os
import time
import json
from app.routers.stats import get_normalized_match

# Delay between requests (safety)
REQUEST_DELAY = 1.2  # seconds


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_matches(match_ids: list[int], league_name: str, season_name: str):
    base_path = f"data/normalized/{league_name}/{season_name}/"

    for match_id in match_ids:
        out_path = f"{base_path}{match_id}.json"

        # Skip if already collected
        if os.path.exists(out_path):
            print(f"[SKIP] {match_id} already collected")
            continue

        print(f"[FETCH] Normalized match {match_id}")

        try:
            normalized = get_normalized_match(match_id)
            save_json(out_path, normalized)
            print(f"[OK] Saved {match_id}")
        except Exception as e:
            print(f"[ERROR] Failed {match_id}: {e}")

        time.sleep(REQUEST_DELAY)
