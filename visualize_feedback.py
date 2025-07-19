import os
import json
import matplotlib.pyplot as plt
from datetime import datetime

FEEDBACK_LOG_PATH = "feedback/feedback_log.json"

def load_feedback():
    if not os.path.exists(FEEDBACK_LOG_PATH):
        print("❌ Feedback log not found.")
        return []

    with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                print("⚠️ Feedback log format is incorrect. Expected a list.")
                return []
            return data
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in feedback log.")
            return []

def parse_feedback_data(feedback):
    chapters = []
    scores = []
    timestamps = []

    for entry in feedback:
        chapter_num = int(entry["chapter"].replace("chapter", ""))
        score = entry["score"]
        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", ""))

        chapters.append(chapter_num)
        scores.append(score)
        timestamps.append(timestamp)

    return chapters, scores, timestamps

def plot_feedback(chapters, scores):
    plt.figure(figsize=(10, 6))
    plt.bar(chapters, scores, color='skyblue')
    plt.title("📊 Chapter Feedback Scores")
    plt.xlabel("Chapter Number")
    plt.ylabel("Score (1–5)")
    plt.xticks(chapters)
    plt.ylim(0, 5.5)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("feedback_scores_bar.png")
    print("📈 Saved bar chart as 'feedback_scores_bar.png'")
    plt.show()

def plot_feedback_over_time(timestamps, scores):
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, scores, marker='o', linestyle='-', color='green')
    plt.title("📉 Feedback Score Trend Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("feedback_scores_time.png")
    print("🕒 Saved time-based chart as 'feedback_scores_time.png'")
    plt.show()

if __name__ == "__main__":
    feedback_data = load_feedback()
    if not feedback_data:
        exit()

    chapters, scores, timestamps = parse_feedback_data(feedback_data)
    plot_feedback(chapters, scores)
    plot_feedback_over_time(timestamps, scores)
