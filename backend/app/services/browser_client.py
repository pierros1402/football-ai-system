import time
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

MOBILE_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SofaScore/6.18.0 (Android; Mobile)",
    "X-Client": "mobile-app",
    "X-App-Version": "6.18.0",
    "X-Platform": "android",
}

class BrowserClient:
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            user_agent=MOBILE_HEADERS["User-Agent"],
            extra_http_headers=MOBILE_HEADERS,
            is_mobile=True,
            viewport={"width": 412, "height": 915},
        )
        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def get_json(self, url: str):
        response = self.page.request.get(url, timeout=20000)
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.json()
