import logging
import json
import re
from typing import Any, Dict, Optional

from app.services.browser_api import BrowserAPI

logger = logging.getLogger(__name__)

NEXT_DATA_REGEX = re.compile(
    r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def extract_next_data_from_html(html: str) -> Optional[Dict[str, Any]]:
    match = NEXT_DATA_REGEX.search(html)
    if not match:
        logger.warning("⚠️ __NEXT_DATA__ script tag not found in HTML")
        return None

    raw_json = match.group(1).strip()

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as e:
        logger.error("❌ Failed to parse __NEXT_DATA__: %s", e)
        return None


def fetch_next_data(browser: BrowserAPI, url: str) -> Optional[Dict[str, Any]]:
    logger.info(f"🌐 Fetching HTML for: {url}")

    # 🔥 1) Πήγαινε στη σελίδα
    try:
        browser.page.goto(url, timeout=30000, wait_until="domcontentloaded")
    except Exception as e:
        logger.warning(f"⚠️ Navigation error: {e}")

    # 🔥 2) Περίμενε να σταματήσουν τα requests
    try:
        browser.page.wait_for_load_state("networkidle", timeout=15000)
    except:
        logger.warning("⚠️ networkidle timeout — continuing anyway")

    # 🔥 3) Πάρε HTML με retry (λόγω hydration)
    html = None
    for _ in range(5):
        try:
            html = browser.page.content()
            break
        except:
            browser.page.wait_for_timeout(300)

    if not html:
        logger.error("❌ Could not retrieve HTML after retries")
        return None

    # 🔥 4) Εξαγωγή JSON
    data = extract_next_data_from_html(html)
    if not data:
        logger.warning("⚠️ No __NEXT_DATA__ extracted")
        return None

    logger.info("✅ __NEXT_DATA__ extracted successfully")
    return data
