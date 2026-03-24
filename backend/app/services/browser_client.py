from playwright.sync_api import sync_playwright
import json

def fetch_safely(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        response = page.goto(url)

        if response is None or response.status != 200:
            browser.close()
            return None

        text = response.text()
        browser.close()

        try:
            return json.loads(text)
        except:
            return None
