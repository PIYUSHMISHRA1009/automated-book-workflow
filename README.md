# 🤖 Automated Book Workflow

A multi-agent AI-powered pipeline that takes in a book chapter URL (like Wikisource), processes it through:

- ✅ Scraping
- ✍️ Rewriting
- 🔍 Reviewing
- 📕 PDF Generation
- 🔊 Text-to-speech narration (MP3)
- 👤 Optional human-in-the-loop editing

## 🧠 Modes

- 🔁 Fully Agentic Mode: All agents work automatically
- 👤 Human-in-the-Loop Mode: You can review/edit rewritten content

## 🚀 How to Run

1. Clone this repo  
   `git clone https://github.com/PIYUSHMISHRA1009/automated-book-workflow.git`

2. Install dependencies  
   `pip install -r requirements.txt`

3. Start the FastAPI backend  
   `uvicorn app.api:app --reload`

4. In a separate terminal, launch Streamlit  
   `streamlit run streamlit_app.py`

## 🧪 Example URLs

- https://en.wikisource.org/wiki/Pride_and_Prejudice/Chapter_1

## 📂 Output

- `*.txt` versions for each agent step
- `*.pdf` for final output
- `*.mp3` for narrated voiceover

---

Made with ❤️ using FastAPI, LangChain, gTTS, PyMuPDF, and Streamlit.
