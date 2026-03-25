def normalize_full_match(full: dict) -> dict:
    event = full["event"]

    league = {
        "id": event["season"]["id"],
        "name": event["season"]["name"],
        "country": event["tournament"]["category"]["name"],
        "season_id": event["season"]["id"],
        "season_name": event["season"]["name"],
    }

    teams = {
        "home": {
            "id": event["homeTeam"]["id"],
            "name": event["homeTeam"]["name"],
            "short_name": event["homeTeam"]["shortName"],
        },
        "away": {
            "id": event["awayTeam"]["id"],
            "name": event["awayTeam"]["name"],
            "short_name": event["awayTeam"]["shortName"],
        },
    }

    result = {
        "home_goals": event["homeScore"].get("current"),
        "away_goals": event["awayScore"].get("current"),
        "winner": "home" if event.get("winnerCode") == 1 else "away" if event.get("winnerCode") == 2 else None,
        "status": event["status"]["description"],
    }

    return {
        "match_id": full["match_id"],
        "league": league,
        "teams": teams,
        "result": result,
        "standings_snapshot": {
            "table": full["standings"] or [],
            "home_row": None,
            "away_row": None,
        },
        "form": {
            "home_last_10": full["form"]["home"] or [],
            "away_last_10": full["form"]["away"] or [],
        },
    }
