import logging
from typing import List, Dict, Any
from app.services.browser_client import BrowserClient

logger = logging.getLogger(__name__)

BASE_API = "https://api.sofascore.com/api/v1"


# ---------------------------------------------------------
# 55 UEFA COUNTRIES (ISO alpha2 + UK subdivisions + Israel)
# ---------------------------------------------------------
UEFA_COUNTRIES = {
    "AL","AD","AM","AT","AZ","BA","BE","BG","BY","CH","CY","CZ","DE","DK","EE",
    "ES","FI","FO","FR","GE","GI","GR","HR","HU","IE","IS","IT","KZ","LI","LT",
    "LU","LV","MC","MD","ME","MK","MT","NL","NO","PL","PT","RO","RS","RU","SE",
    "SI","SK","SM","TR","UA",
    # UK subdivisions
    "GB-ENG","GB-SCT","GB-WLS","GB-NIR",
    # Israel (UEFA member)
    "IL"
}


# ---------------------------------------------------------
# FILTER HELPERS
# ---------------------------------------------------------

def is_youth(name: str) -> bool:
    terms = ["u17","u18","u19","u20","u21","u23","youth","academy","juvenil","junior"]
    name = name.lower()
    return any(t in name for t in terms)


def is_regional_cup(name: str) -> bool:
    terms = [
        "regional", "county", "district", "local", "amateur",
        "state cup", "provinc", "depart", "metropolitan",
        "catalunya", "galicia", "andalu", "paulista",
        "federacion", "federation", "liga regional",
        "copa regional", "regional cup"
    ]
    name = name.lower()
    return any(t in name for t in terms)


def is_low_tier(name: str) -> bool:
    terms = [
        "division 3", "division 4", "division 5", "division 6",
        "serie d", "serie e",
        "non league", "amateur league"
    ]
    name = name.lower()
    return any(t in name for t in terms)


def is_top_international(name: str) -> bool:
    terms = [
        "world cup", "euro", "copa america", "africa cup", "asian cup",
        "gold cup", "nations league",
        "champions league", "sudamericana",
        "champions cup", "afc champions", "caf champions", "ofc champions"
    ]
    name = name.lower()
    return any(t in name for t in terms)


# ---------------------------------------------------------
# API HELPERS (your existing functions)
# ---------------------------------------------------------

def fetch_unique_tournament(client: BrowserClient, ut_id: int):
    url = f"{BASE_API}/unique-tournament/{ut_id}"
    logger.info("REQUEST: %s", url)
    return client.get_json(url)


def fetch_season_events(client: BrowserClient, ut_id: int, season_id: int = None):
    if season_id is None:
        ut = fetch_unique_tournament(client, ut_id)
        season_id = ut["uniqueTournament"]["currentSeason"]["id"]

    url = f"{BASE_API}/unique-tournament/{ut_id}/season/{season_id}/events"
    logger.info("REQUEST: %s", url)
    data = client.get_json(url)
    return data.get("events", [])


# ---------------------------------------------------------
# DISCOVER ALL LEAGUES (MAIN FUNCTION)
# ---------------------------------------------------------

def discover_leagues() -> List[Dict[str, Any]]:
    """
    Επιστρέφει όλες τις διοργανώσεις που θέλουμε:
    - UEFA 55 χώρες → full depth
    - Εκτός UEFA → κόβουμε low tiers
    - Youth → κόβεται παντού
    - Regional cups → κόβονται παντού
    - International → κρατάμε μόνο top
    """

    url = f"{BASE_API}/sport/football/categories"
    logger.info("REQUEST: %s", url)

    with BrowserClient() as client:
        data = client.get_json(url)

    categories = data.get("categories", [])
    leagues = []

    for cat in categories:
        country = cat.get("country", {})
        alpha2 = country.get("alpha2", "")
        tournaments = cat.get("tournaments", [])

        for t in tournaments:
            name = t.get("name", "")
            ut = t.get("uniqueTournament", {})
            ut_id = ut.get("id")
            ut_name = ut.get("name", "")

            # Youth → skip
            if is_youth(name) or is_youth(ut_name):
                continue

            # Regional cups → skip
            if is_regional_cup(name) or is_regional_cup(ut_name):
                continue

            # International tournaments (no country)
            if not alpha2:
                if not is_top_international(name) and not is_top_international(ut_name):
                    continue

            # Low tiers → skip ONLY outside UEFA
            if alpha2 not in UEFA_COUNTRIES:
                if is_low_tier(name) or is_low_tier(ut_name):
                    continue

            # Valid league
            leagues.append({
                "id": ut_id,
                "name": ut_name or name,
                "country": alpha2,
            })

    return leagues

# ---------------------------------------------------------
# DISCOVER SEASONS (MAIN FUNCTION)
# ---------------------------------------------------------
def discover_seasons(client: BrowserClient, ut_id: int, years_back: int = 10):
    """
    Επιστρέφει τις σεζόν ενός unique tournament (ut_id) με τους εξής περιορισμούς:
    - Youth seasons → κόβονται
    - Τοπικά/περιφερειακά κύπελλα → κόβονται
    - Μικρές κατηγορίες εκτός Ευρώπης → κόβονται (handled already in discover_leagues)
    - Σεζόν 25–26 → προτεραιότητα
    - Ιστορικό 5–10 χρόνια → μέσα
    """

    ut = fetch_unique_tournament(client, ut_id)
    seasons = ut["uniqueTournament"].get("seasons", [])

    valid_seasons = []
    priority_seasons = []

    for s in seasons:
        season_name = s.get("name", "").lower()
        season_id = s.get("id")

        # Youth seasons → skip
        if is_youth(season_name):
            continue

        # Τοπικά κύπελλα → skip (αν υπάρχουν στο όνομα)
        if is_regional_cup(season_name):
            continue

        # Προτεραιότητα: 25–26
        if "25/26" in season_name or "2025" in season_name:
            priority_seasons.append({
                "id": season_id,
                "name": s.get("name"),
                "year": s.get("year"),
            })
            continue

        # Ιστορικό 5–10 χρόνια
        # Το Sofascore δίνει year ως string "2021", "2022", "24/25" κτλ.
        year_str = s.get("year") or s.get("name")
        if not year_str:
            continue

        # Extract numeric year safely
        digits = "".join(ch for ch in year_str if ch.isdigit())
        if len(digits) >= 4:
            year = int(digits[:4])
        else:
            continue

        if 2015 <= year <= 2025:  # 10 χρόνια πίσω
            valid_seasons.append({
                "id": season_id,
                "name": s.get("name"),
                "year": s.get("year"),
            })

    # Βάζουμε πρώτα την 25–26
    return priority_seasons + valid_seasons


# ---------------------------------------------------------
# DISCOVER SEASON MATCHES (MAIN FUNCTION)
# ---------------------------------------------------------
def fetch_season_matches(
    client: BrowserClient,
    ut_id: int,
    season_id: int,
    include_upcoming: bool = True,
    include_finished: bool = True
) -> List[int]:
    """
    Επιστρέφει ΟΛΑ τα match_ids μιας σεζόν, με πλήρη υποστήριξη:
    - Finished matches
    - Upcoming matches
    - Playoffs / Playouts / Μπαράζ
    - Knockout rounds
    - Qualification rounds
    - Χωρίς youth, regional cups, low tiers (έχουν ήδη κοπεί στο discovery)
    """

    events = fetch_season_events(client, ut_id, season_id)
    match_ids = []

    for e in events:
        status = e.get("status", {})
        status_type = status.get("type", "").lower()
        status_code = status.get("code")

        # Youth events → skip
        name = e.get("tournament", {}).get("name", "")
        if is_youth(name):
            continue

        # Regional cups → skip
        if is_regional_cup(name):
            continue

        # Finished matches
        if include_finished and status_type == "finished":
            match_ids.append(e["id"])
            continue

        # Upcoming matches
        if include_upcoming and status_type in ["notstarted", "inprogress"]:
            match_ids.append(e["id"])
            continue

        # Knockout / playoffs / qualifiers
        round_info = e.get("roundInfo", {})
        cup_type = round_info.get("cupRoundType")

        if cup_type is not None:
            # Είναι knockout round → πάντα μέσα
            match_ids.append(e["id"])
            continue

        # Qualification rounds (π.χ. Champions League qualifiers)
        if "qualification" in round_info.get("slug", "").lower():
            match_ids.append(e["id"])
            continue

        # Playoffs / Playouts
        if "playoff" in round_info.get("name", "").lower():
            match_ids.append(e["id"])
            continue

        if "play-out" in round_info.get("name", "").lower():
            match_ids.append(e["id"])
            continue

    return match_ids
