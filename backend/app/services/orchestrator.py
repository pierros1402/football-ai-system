from app.services.discovery import (
    fetch_all_tournaments,
    fetch_tournament_seasons,
    get_current_or_upcoming_season
)
from app.services.league_fetcher import fetch_league_matches
from app.services.collector import collect_matches


def collect_all_leagues():
    tournaments = fetch_all_tournaments()

    for t in tournaments:
        tid = t["id"]
        t_name = t["name"]
        country = (t.get("category") or {}).get("name", "Unknown")

        print(f"\n=== LEAGUE: {t_name} ({country}) ===")

        # 1️⃣ Fetch seasons for this league
        seasons = fetch_tournament_seasons(tid)
        if not seasons:
            print("No seasons found, skipping.")
            continue

        # 2️⃣ Pick current or upcoming season
        season = get_current_or_upcoming_season(seasons)
        if not season:
            print("No active/upcoming season, skipping.")
            continue

        sid = season["id"]
        s_name = season["name"]

        print(f"Using season: {s_name} (ID: {sid})")

        # 3️⃣ Fetch all match IDs (regular + playoff + playout + groups)
        match_ids = fetch_league_matches(tid, sid)
        if not match_ids:
            print("No matches found, skipping.")
            continue

        print(f"Found {len(match_ids)} matches.")

        # 4️⃣ Collect normalized data
        safe_league_name = t_name.replace("/", "-").replace(" ", "_")
        safe_season_name = s_name.replace("/", "-").replace(" ", "_")

        collect_matches(
            match_ids,
            league_name=safe_league_name,
            season_name=safe_season_name
        )

    print("\n=== DONE: All leagues processed ===")
