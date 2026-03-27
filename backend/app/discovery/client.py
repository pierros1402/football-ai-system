import asyncio
import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class SofascoreClient:
    BASE_URL = "https://api.sofascore.com/api/v1"

    def __init__(self, timeout: float = 10.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

        # Browser-like headers to bypass Sofascore 403
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.sofascore.com",
            "Referer": "https://www.sofascore.com/",
            "X-Requested-With": "XMLHttpRequest",
        }

        self.client = httpx.AsyncClient(timeout=timeout, headers=self.headers)

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.request(
                    method,
                    url,
                    params=params,
                    headers=self.headers,  # ensure headers always included
                )

                # Sofascore rate limit
                if response.status_code == 429:
                    wait = 1.5 * attempt
                    logger.warning(f"Rate limit hit. Waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                logger.error(f"Network error on attempt {attempt}: {e}")
                await asyncio.sleep(1.2 * attempt)

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.error(f"HTTP error {status}: {e}")

                # Retry only for 5xx
                if 500 <= status < 600:
                    await asyncio.sleep(1.5 * attempt)
                    continue

                # 403, 404, 401 → do not retry
                raise

        raise RuntimeError(f"Failed after {self.max_retries} attempts: {url}")

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return await self._request("GET", endpoint, params)

    async def close(self):
        await self.client.aclose()
