import os
import re
import sys
import json
import asyncio
import logging
from urllib.parse import urljoin
from fpdf import FPDF
from playwright.async_api import async_playwright
import httpx
from dotenv import load_dotenv

from ai.human_feedback import load_feedback, save_feedback
from ai.embeddings import store_chapter_embedding
from ai.voice import speak, listen

# === ENV & CONSTANTS ===
load_dotenv()
FONT_NAME = "DejaVu"
FONT_PATH = os.path.join("fonts", "DejaVuSans.ttf")
OUTPUT_PDF = "book_output.pdf"
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("❌ Set your API key as an environment variable: OPENROUTER_API_KEY")

logging.basicConfig(filename="main_ai.log", level=logging.INFO)


def clean_filename(text):
    return re.sub(r"[\\/*?\"<>|]", "", text)


def save_pdf(chapters):
    if not os.path.isfile(FONT_PATH):
        raise FileNotFoundError(f"Missing font at {FONT_PATH}")

    pdf = FPDF()
    pdf.add_font(FONT_NAME, "", FONT_PATH, uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, chapter in enumerate(chapters, 1):
        pdf.add_page()
        pdf.set_font(FONT_NAME, size=14)
        pdf.multi_cell(0, 10, f"Chapter {i}: {chapter['title']}\n\n")
        pdf.set_font(FONT_NAME, size=11)
        pdf.multi_cell(0, 8, chapter["content"])

    pdf.output(OUTPUT_PDF)
    print(f"📘 PDF saved: {OUTPUT_PDF}")


def generate_adaptive_prompt(score_avg):
    if score_avg >= 4.5:
        return (
            "You are an expert AI author. Rewrite the chapter in a modern, engaging tone. Keep structure simple and vibrant. "
            "You’ve been receiving high praise, so keep being bold and creative!"
        )
    elif score_avg >= 3:
        return (
            "You are an AI rewriting chapters for readability and clarity. Keep tone modern and structure logical. "
            "Be cautious about over-simplifying—previous feedback suggests some inconsistencies."
        )
    else:
        return (
            "You are an AI assistant rewriting this chapter to fix clarity, coherence, and flow. Previous rewrites were not good. "
            "This time, prioritize readability and logical structure. Avoid filler and be more expressive."
        )


async def spin_chapter(text, chapter_num, score_avg):
    prompt = generate_adaptive_prompt(score_avg)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Rewrite and review this:\n\n{text[:8000]}"}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            return content
    except Exception as e:
        print(f"❌ API error: {e}")
        return "Rewrite failed."


def compute_feedback_average():
    feedback = load_feedback()
    if not isinstance(feedback, list) or len(feedback) == 0:
        return 3.0  # Default neutral
    scores = [entry["score"] for entry in feedback if isinstance(entry.get("score"), int)]
    return sum(scores) / len(scores) if scores else 3.0


async def scrape_and_process(start_url):
    chapters = []
    visited = set()
    current_url = start_url
    chapter_num = 1

    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("chapters", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.webkit.launch()
        context = await browser.new_context()

        while current_url and current_url not in visited:
            visited.add(current_url)
            print(f"\n✅ Processing chapter {chapter_num}: {current_url}")

            page = await context.new_page()
            await page.goto(current_url)

            title = await page.title()
            clean_title = title.replace(" - Wikisource, the free online library", "")
            content = await page.inner_text("div#mw-content-text")

            raw_path = f"chapters/chapter{chapter_num}.txt"
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(content)

            screenshot_path = f"screenshots/chapter{chapter_num}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Saved screenshot")

            score_avg = compute_feedback_average()
            print("✍️ Rewriting chapter with LLM...")
            rewritten_output = await spin_chapter(content, chapter_num, score_avg)

            reviewed_path = f"chapters/chapter{chapter_num}_reviewed.txt"
            with open(reviewed_path, "w", encoding="utf-8") as f:
                f.write(rewritten_output)

            print("=" * 60)
            print(f"🧾 Reviewed Output for Chapter {chapter_num}:\n")
            print(rewritten_output[:1000] + ("..." if len(rewritten_output) > 1000 else ""))
            print("=" * 60)

            speak("Chapter rewrite complete. Say approve, edit, or regenerate. Then rate 1 to 5.")
            attempts = 0
            while attempts < 3:
                user_command = listen().lower().strip()
                if any(x in user_command for x in ["approve", "edit", "regenerate"]):
                    break
                speak("Didn't catch that. Say approve, edit, or regenerate.")
                attempts += 1

            feedback_score = 3
            decision = "a"

            if "edit" in user_command:
                decision = "e"
            elif "regenerate" in user_command:
                decision = "r"

            for word in user_command.split():
                if word.isdigit() and 1 <= int(word) <= 5:
                    feedback_score = int(word)
                    break

            if decision == "e":
                print(f"Please manually edit the file: {reviewed_path}")
                speak("Please edit the file and press Enter when done.")
                input("🔧 Press Enter after editing...")

            try:
                save_feedback(chapter_num, decision, feedback_score)
            except Exception as e:
                print(f"⚠️ Could not save feedback: {e}")

            try:
                store_chapter_embedding(
                    chapter_num=chapter_num,
                    title=clean_title,
                    content=rewritten_output,
                    feedback_score=feedback_score
                )
            except Exception as e:
                print(f"⚠️ Failed to store embedding: {e}")

            chapters.append({
                "title": clean_title,
                "content": rewritten_output
            })

            next_link = await page.query_selector('a:has-text("→")')
            if next_link:
                href = await next_link.get_attribute("href")
                next_url = urljoin(current_url, href)
                if next_url in visited:
                    print("🛑 Loop detected. Stopping.")
                    break
                current_url = next_url
                chapter_num += 1
            else:
                print("🏁 No next chapter found. Scraping complete.")
                break

            await page.close()

        await browser.close()
        return chapters


# === ENTRY POINT ===
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main_ai.py <starting_url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"🚀 Starting from: {url}")
    chapters = asyncio.run(scrape_and_process(url))
    if chapters:
        save_pdf(chapters)
        print("✅ PDF generation complete.")
