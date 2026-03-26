def parse_tournament(page_props):
    """
    Επιστρέφει βασικές πληροφορίες για το tournament.
    """
    ut = page_props.get("initialProps", {}).get("uniqueTournament", {})
    return {
        "id": ut.get("id"),
        "name": ut.get("name"),
        "slug": ut.get("slug"),
        "category": ut.get("category", {}),
        "tier": ut.get("tier"),
    }


def parse_seasons(page_props):
    """
    Επιστρέφει όλες τις seasons του tournament.
    """
    # Συνήθως εδώ
    seasons = (
        page_props.get("initialState", {})
        .get("uniqueTournament", {})
        .get("seasons", [])
    )

    # fallback
    if not seasons:
        seasons = page_props.get("initialProps", {}).get("seasons", [])

    return seasons


def parse_matches(page_props):
    """
    Επιστρέφει όλα τα matches της σελίδας (αν υπάρχουν).
    """
    events = (
        page_props.get("initialState", {})
        .get("events", [])
    )

    return events
