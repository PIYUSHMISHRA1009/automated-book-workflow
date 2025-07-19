# ai/editor.py
from dotenv import load_dotenv
load_dotenv()

import openai
import os
import json
from datetime import datetime

# Optional: Debug check to ensure API key is being loaded
# print("[DEBUG] OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # ✅ Correct key name
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

FEEDBACK_FILE = "feedback/feedback_log.json"

def get_avg_feedback_score():
    if not os.path.exists(FEEDBACK_FILE):
        return 3  # Default neutral score
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            scores = [entry["score"] for entry in data if "score" in entry]
            return sum(scores) / len(scores) if scores else 3
    except Exception as e:
        print(f"[ERROR] Failed to read feedback file: {e}")
        return 3

def adapt_editor_instruction(avg_score: float) -> str:
    if avg_score <= 2:
        return "Make the text more emotionally engaging, vivid, and human-like."
    elif avg_score >= 4:
        return "Refine the language to be clear, concise, and professional."
    else:
        return "Enhance clarity and structure while keeping the original tone."

def edit_chapter(rewritten_text: str) -> str:
    avg_score = get_avg_feedback_score()
    instruction = adapt_editor_instruction(avg_score)

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert copy editor. {instruction}"
            },
            {
                "role": "user",
                "content": f"Please edit the following passage for grammar, flow, and clarity:\n\n{rewritten_text}"
            }
        ],
        temperature=0.7,
        max_tokens=4096
    )
    return response.choices[0].message.content
