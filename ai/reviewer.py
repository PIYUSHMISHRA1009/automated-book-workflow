# ai/reviewer.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env values

client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

def review_chapter(text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {
                "role": "system",
                "content": "You are a careful editor checking the rewritten text for flow, grammar, and tone consistency. Provide constructive review and suggestions inline."
            },
            {
                "role": "user",
                "content": f"Please review the following chapter:\n\n{text}"
            }
        ],
        temperature=0.5,
        max_tokens=4096
    )
    return response.choices[0].message.content
