````markdown
# 📘 Automated Book Workflow with Agentic AI Pipeline

This project builds an end-to-end AI-powered system to scrape book chapters (e.g. from Wikisource), rewrite them using LLMs, review, edit, and convert into downloadable **PDFs**, **audio**, and **embeddings** — with support for both **fully automated** and **human-in-the-loop** review modes.

## 🔧 Features

- 🕸️ Web Scraping with Screenshot Capture
- ✍️ LLM-based Rewriting (OpenAI or other)
- 🧠 Reviewer Agent for Quality Check
- 🪄 Final Editor Agent
- 📊 Feedback Logging
- 🧬 Vector Embedding Storage
- 📕 PDF Generation
- 🔊 Text-to-Speech (MP3)
- 🖥️ Streamlit Frontend with 2 Modes:
  - 🔁 Fully Agentic (Auto)
  - 👤 Human-in-the-loop (Manual Editing)

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/PIYUSHMISHRA1009/automated-book-workflow.git
cd automated-book-workflow
````

### 2. Create & activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI backend

```bash
uvicorn api:app --reload
```

### 5. In a separate terminal, start the Streamlit frontend

```bash
streamlit run streamlit_app.py
```

## 📂 Folder Structure

```
├── ai/
│   ├── writer.py
│   ├── reviewer.py
│   ├── editor.py
│   ├── embeddings.py
│   ├── voice.py
│   └── human_feedback.py
├── scraping/
│   └── scraper.py
├── static/
│   └── (PDFs, screenshots, MP3s)
├── chapters/
│   └── (Generated text files)
├── utils/
│   └── pdf_utils.py
├── api.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```
