import logging
import json
import time
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class BrowserAPI:
    def __init__(self, headless=True):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )
        self.page = self.context.new_page()

        # Load homepage to get cookies + anti-bot
        try:
            self.page.goto("https://www.sofascore.com", timeout=15000, wait_until="domcontentloaded")
        except:
            logger.warning("⚠️ Sofascore homepage timeout — continuing anyway...")

        time.sleep(1.2)

    # ---------------------------------------------------------
    # NETWORK INTERCEPTION FOR TOURNAMENT DISCOVERY
    # ---------------------------------------------------------
    def intercept_tournaments(self):
        captured = []

        def handler(response):
            try:
                url = response.url
                if "tournament" not in url:
                    return

                ct = response.headers.get("content-type", "")
                if "application/json" not in ct:
                    return

                data = response.json()
                captured.append(data)
            except:
                pass

        return captured, handler

    # ---------------------------------------------------------
    # FETCH JSON USING PAGE CONTEXT (WITH REAL COOKIES)
    # ---------------------------------------------------------
    def get_json(self, url):
        logger.info(f"REQUEST: {url}")

        script = """
            async (url) => {
                const res = await fetch(url, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json",
                        "User-Agent": navigator.userAgent
                    }
                });

                const text = await res.text();
                return { status: res.status, body: text };
            }
        """

        result = self.page.evaluate(script, url)

        logger.info(f"STATUS: {result['status']}")
        logger.info(f"BODY: {result['body'][:500]}")

        if result["status"] != 200:
            return None

        try:
            return json.loads(result["body"])
        except:
            return None

    def close(self):
        self.browser.close()
        self.p.stop()
