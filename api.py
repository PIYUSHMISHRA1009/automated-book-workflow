import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from scraping.scraper import scrape_chapter
from ai.writer import rewrite_chapter
from ai.reviewer import review_chapter
from ai.editor import edit_chapter
from ai.human_feedback import log_feedback
from ai.embeddings import store_chapter_embedding
from ai.voice import text_to_speech
from utils.pdf_utils import generate_pdf
from dotenv import load_dotenv
from pathlib import Path
import uuid

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format="🔧 [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === Load environment variables ===
load_dotenv()

# === FastAPI app setup ===
app = FastAPI()

# Serve static files like PDFs, MP3s, Screenshots
app.mount("/static", StaticFiles(directory="static"), name="static")

# === Request model ===
class ChapterRequest(BaseModel):
    url: str
    feedback_score: int = 5

# === POST: Process Chapter ===
@app.post("/process-agentic/")
def process_chapter(request: ChapterRequest):
    chapter_id = str(uuid.uuid4())[:8]
    base_name = f"chapter_{chapter_id}"
    base_dir = Path("chapters")
    static_dir = Path("static")
    base_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(exist_ok=True)

    raw_path = base_dir / f"{base_name}.txt"
    screenshot_path = static_dir / f"{base_name}.png"
    rewritten_path = base_dir / f"{base_name}_rewritten.txt"
    reviewed_path = base_dir / f"{base_name}_reviewed.txt"
    final_txt_path = base_dir / f"{base_name}_final.txt"
    pdf_path = static_dir / f"{base_name}_final.pdf"
    audio_path = static_dir / f"{base_name}.mp3"

    logger.info(f"📥 Starting processing for: {request.url}")

    # === 1. Scrape chapter ===
    logger.info("🌐 Scraping and taking screenshot...")
    scraped_txt_path, _ = scrape_chapter(request.url, raw_path, screenshot_path)
    raw_text = Path(scraped_txt_path).read_text(encoding="utf-8")

    # === 2. Rewrite ===
    logger.info("✍️ Rewriting chapter with LLM...")
    rewritten = rewrite_chapter(raw_text)
    rewritten_path.write_text(rewritten, encoding="utf-8")

    # === 3. Review ===
    logger.info("🧠 Reviewing the rewritten content...")
    reviewed = review_chapter(rewritten)
    reviewed_path.write_text(reviewed, encoding="utf-8")

    # === 4. Edit ===
    logger.info("🪄 Editing reviewed content...")
    final_text = edit_chapter(reviewed)
    final_txt_path.write_text(final_text, encoding="utf-8")

    # === 5. Log Feedback ===
    logger.info(f"📊 Logging feedback: {request.feedback_score}/5")
    log_feedback(score=request.feedback_score, context=str(final_txt_path))

    # === 6. Embedding for search ===
    logger.info("🧬 Storing chapter embeddings for search...")
    store_chapter_embedding(
        title=f"Chapter {chapter_id}",
        content=final_text,
        feedback_score=request.feedback_score,
        chapter_num=chapter_id
    )

    # === 7. Generate PDF ===
    logger.info("📄 Generating PDF output...")
    generate_pdf(
        content=final_text,
        title=f"Chapter {chapter_id}",
        output_path=str(pdf_path)
    )

    # === 8. Text to Speech ===
    logger.info("🔊 Generating audio narration...")
    text_to_speech(final_text, str(audio_path))

    logger.info(f"✅ All steps completed for Chapter {chapter_id}")

    return {
        "status": "success",
        "chapter_id": chapter_id,
        "message": "✅ Chapter processed end-to-end",
        "final_text_file": str(final_txt_path),
        "pdf_file": str(pdf_path),
        "audio_file": str(audio_path),
        "screenshot": str(screenshot_path)
    }

# === GET: Root ===
@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h2>✅ Automated Book Workflow API is running!</h2>"

# === GET: View Chapter Output ===
@app.get("/view/{chapter_id}", response_class=HTMLResponse)
def view_output(chapter_id: str):
    base_name = f"chapter_{chapter_id}"
    pdf_path = f"/static/{base_name}_final.pdf"
    audio_path = f"/static/{base_name}.mp3"
    screenshot_path = f"/static/{base_name}.png"

    return f"""
    <html>
        <head><title>Chapter Output</title></head>
        <body>
            <h2>📘 Final Chapter Output</h2>
            <iframe src="{pdf_path}" width="100%" height="600px"></iframe><br>
            <a href="{pdf_path}" download>⬇️ Download PDF</a><br><br>

            <h3>🔊 Listen to Audio:</h3>
            <audio controls>
                <source src="{audio_path}" type="audio/mpeg">
                Your browser does not support the audio tag.
            </audio><br><br>

            <h3>🖼️ Screenshot Taken During Scrape:</h3>
            <img src="{screenshot_path}" width="600px"><br><br>

            <a href="/">🔙 Back to Home</a>
        </body>
    </html>
    """
