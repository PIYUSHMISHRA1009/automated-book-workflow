# scraping/scraper.py

from playwright.sync_api import sync_playwright
import os

def scrape_chapter(url: str, save_text_path: str, screenshot_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless=True for production
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        # Save screenshot
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=True)

        # Get and save text (try multiple selectors for robustness)
        content = page.locator("div#mw-content-text").inner_text()
        if not content:
            raise ValueError("❌ Could not find content on page. Check selector or structure.")

        os.makedirs(os.path.dirname(save_text_path), exist_ok=True)
        with open(save_text_path, "w", encoding="utf-8") as f:
            f.write(content)

        browser.close()
        print(f"✅ Scraped and saved: {url}")

        # ✅ Return paths so api.py can unpack them
        return save_text_path, screenshot_path
