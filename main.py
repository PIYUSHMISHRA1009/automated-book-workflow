# main.py

import os
from scraping.scraper import scrape_chapter

def process_chapter_from_url(url: str):
    """
    Scrapes a chapter from a URL and returns the paths to saved text and screenshot.
    """
    # Generate a clean chapter ID from URL
    chapter_id = url.strip("/").split("/")[-1].replace(" ", "_").replace("-", "_")

    os.makedirs("chapters", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    text_path = f"chapters/{chapter_id}.txt"
    screenshot_path = f"screenshots/{chapter_id}.png"

    scrape_chapter(
        url=url,
        save_text_path=text_path,
        screenshot_path=screenshot_path
    )

    return text_path, screenshot_path

# For manual test runs
if __name__ == "__main__":
    url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
    process_chapter_from_url(url)
