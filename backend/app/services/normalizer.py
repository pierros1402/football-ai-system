def normalize_full_match(raw: dict) -> dict:
    event = raw.get("event") or {}
    standings = raw.get("standings") or []
    form = raw.get("form") or {}

    # League / season
    unique_tournament = event.get("uniqueTournament") or {}
    tournament = event.get("tournament") or {}
    season = event.get("season") or {}

    league = {
        "id": unique_tournament.get("id"),
        "name": unique_tournament.get("name"),
        "country": (unique_tournament.get("category") or {}).get("name"),
        "season_id": season.get("id"),
        "season_name": season.get("name"),
    }

    # Teams
    home_team = event.get("homeTeam") or {}
    away_team = event.get("awayTeam") or {}

    teams = {
        "home": {
            "id": home_team.get("id"),
            "name": home_team.get("name"),
            "short_name": home_team.get("shortName"),
        },
        "away": {
            "id": away_team.get("id"),
            "name": away_team.get("name"),
            "short_name": away_team.get("shortName"),
        },
    }

    # Result
    home_score = (event.get("homeScore") or {}).get("normaltime")
    away_score = (event.get("awayScore") or {}).get("normaltime")

    if home_score is not None and away_score is not None:
        if home_score > away_score:
            winner = "home"
        elif away_score > home_score:
            winner = "away"
        else:
            winner = "draw"
    else:
        winner = None

    result = {
        "home_goals": home_score,
        "away_goals": away_score,
        "winner": winner,
        "status": (event.get("status") or {}).get("description"),
    }

    # Standings snapshot: full table + rows for home/away
    home_row = None
    away_row = None

    # Sofascore standings structure: standings -> [ { "rows": [...] } ]
    table = []
    if isinstance(standings, list) and len(standings) > 0:
        # παίρνουμε το πρώτο group (συνήθως η βασική βαθμολογία)
        group = standings[0]
        rows = group.get("rows") or []
        table = rows

        home_id = teams["home"]["id"]
        away_id = teams["away"]["id"]

        for row in rows:
            team = (row.get("team") or {})
            tid = team.get("id")
            if tid == home_id:
                home_row = row
            if tid == away_id:
                away_row = row

    standings_snapshot = {
        "table": table,
        "home_row": home_row,
        "away_row": away_row,
    }

    # Form
    home_form_raw = (form.get("home") or [])
    away_form_raw = (form.get("away") or [])

    form_block = {
        "home_last_10": home_form_raw,
        "away_last_10": away_form_raw,
    }

    # Meta
    venue = (event.get("venue") or {}).get("name")
    referee = (event.get("referee") or {}).get("name")

    meta = {
        "kickoff_timestamp": event.get("startTimestamp"),
        "venue": venue,
        "referee": referee,
        "slug": event.get("slug"),
    }

    return {
        "match_id": raw.get("match_id"),
        "league": league,
        "teams": teams,
        "result": result,
        "standings_snapshot": standings_snapshot,
        "form": form_block,
        "meta": meta,
    }
