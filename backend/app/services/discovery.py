from app.services.browser_client import fetch_safely

TOURNAMENTS_URL = "https://api.sofascore.com/api/v1/unique-tournaments"
SEASONS_URL = "https://api.sofascore.com/api/v1/unique-tournament/{tid}/seasons"


def fetch_all_tournaments():
    print("REQUEST ALL TOURNAMENTS:", TOURNAMENTS_URL)
    data = fetch_safely(TOURNAMENTS_URL)
    if not data:
        return []

    return data.get("uniqueTournaments") or []


def fetch_tournament_seasons(tournament_id: int):
    url = SEASONS_URL.format(tid=tournament_id)
    print("REQUEST SEASONS:", url)
    data = fetch_safely(url)
    if not data:
        return []

    return data.get("seasons") or []


def get_current_or_upcoming_season(seasons: list):
    """
    Επιλέγει:
    - ongoing season αν υπάρχει
    - αλλιώς upcoming season
    """

    for s in seasons:
        if s.get("status") == "ongoing":
            return s

    for s in seasons:
        if s.get("status") == "notstarted":
            return s

    return None
