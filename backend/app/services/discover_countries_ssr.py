import logging
from app.services.ssr_discovery import fetch_next_data

logger = logging.getLogger(__name__)

def discover_all_countries(browser):
    url = "https://www.sofascore.com/el/football"
    logger.info("🌍 Fetching ALL countries...")

    data = fetch_next_data(browser, url)
    if not data:
        return []

    page_props = data["props"]["pageProps"]

    # Οι χώρες είναι εδώ:
    # pageProps["initialState"]["sport"]["categories"]
    countries = (
        page_props.get("initialState", {})
        .get("sport", {})
        .get("categories", [])
    )

    logger.info(f"📌 Found {len(countries)} countries")
    return countries
