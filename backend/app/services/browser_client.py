import json
import logging
from contextlib import AbstractContextManager
from typing import Any, Dict, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_MS = 15000
BASE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
}


class BrowserClient(AbstractContextManager):
    def __init__(self, max_retries: int = 3, timeout_ms: int = DEFAULT_TIMEOUT_MS, headless: bool = True):
        self.max_retries = max_retries
        self.timeout_ms = timeout_ms
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._context = None

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(extra_http_headers=BASE_HEADERS)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def get_json(self, url: str) -> Dict[str, Any]:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                page = self._context.new_page()
                response = page.goto(url, timeout=self.timeout_ms, wait_until="networkidle")

                if response is None:
                    raise RuntimeError(f"No response for {url}")

                if response.status != 200:
                    raise RuntimeError(f"Non-200 status {response.status} for {url}")

                text = response.text()
                page.close()
                return json.loads(text)

            except Exception as e:
                last_error = e
                logger.warning(f"Error fetching {url} (attempt {attempt}/{self.max_retries}): {e}")

        raise RuntimeError(f"Failed to fetch {url}") from last_error
