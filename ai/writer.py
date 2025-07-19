from dotenv import load_dotenv
load_dotenv()

import os
import openai
import json
from datetime import datetime

# Initialize OpenAI client using environment variables
client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

FEEDBACK_FILE = "feedback/feedback_log.json"

def get_avg_feedback_score():
    if not os.path.exists(FEEDBACK_FILE):
        return 3  # Neutral default
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            scores = [entry["score"] for entry in data if "score" in entry]
            return sum(scores) / len(scores) if scores else 3
    except:
        return 3

def adapt_prompt_style(avg_score: float) -> str:
    if avg_score <= 2:
        return "Add vivid imagery, enhance emotion, and make it highly engaging and descriptive."
    elif avg_score >= 4:
        return "Polish the writing for clarity and brevity in a minimalist, refined tone."
    else:
        return "Modernize the language while preserving the story's original tone and meaning."

def rewrite_chapter(original_text: str) -> str:
    avg_score = get_avg_feedback_score()
    style_instruction = adapt_prompt_style(avg_score)

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert AI writer. {style_instruction}"
            },
            {
                "role": "user",
                "content": f"Rewrite the following passage:\n\n{original_text}"
            }
        ],
        temperature=0.8,
        max_tokens=4096
    )
    return response.choices[0].message.content
