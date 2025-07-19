import os
import json
from datetime import datetime

# === Constants ===
FEEDBACK_LOG_PATH = "feedback/feedback_log.json"
os.makedirs("feedback", exist_ok=True)

# === Load Existing Feedback Log ===
def load_feedback():
    if os.path.exists(FEEDBACK_LOG_PATH):
        try:
            with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    print("⚠️ Warning: Feedback log was not a list. Resetting.")
                    return []
        except json.JSONDecodeError:
            print("⚠️ Warning: Feedback log is corrupted. Starting fresh.")
            return []
    return []

# === Save Feedback Entry ===
def save_feedback(chapter_num, decision, score):
    logs = load_feedback()

    feedback_entry = {
        "chapter": f"chapter{chapter_num}",
        "decision": decision,
        "score": score,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    logs.append(feedback_entry)

    with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    print(f"✅ Score {score}/5 recorded for Chapter {chapter_num}")

# === Unified Logger Used in API ===
def log_feedback(score: int, context: str = ""):
    logs = load_feedback()

    feedback_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "score": score,
        "context": context  # Changed from "comment" to "context"
    }

    logs.append(feedback_entry)

    with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    print(f"✅ Feedback score {score}/5 logged successfully.")
