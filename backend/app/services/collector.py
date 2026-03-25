import os
import json
from app.services.stats_service import get_normalized_match


def collect_matches(match_ids: list[int], league_name: str, season_name: str):
    base_path = f"data/normalized/{league_name}/{season_name}"
    os.makedirs(base_path, exist_ok=True)

    for match_id in match_ids:
        try:
            normalized = get_normalized_match(match_id)
            out_path = f"{base_path}/{match_id}.json"

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(normalized, f, ensure_ascii=False, indent=2)

            print(f"[OK] Saved normalized match {match_id}")

        except Exception as e:
            print(f"[ERROR] Failed match {match_id}: {e}")
