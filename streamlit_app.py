# streamlit_app.py

import streamlit as st
import requests
import os
from pathlib import Path

BASE_API = "http://localhost:8000"

st.set_page_config(page_title="📘 AI-Powered Book Chapter Processor", layout="wide")
st.title("📚 Automated Book Workflow")

# === Helper to Show All Outputs (Auto Mode) ===
def show_output(data, chapter_id):
    final_file = Path(data["final_text_file"])
    base_path = final_file.with_name(final_file.stem.replace("_final", ""))
    pdf_file = data["pdf_file"]
    audio_file = data["audio_file"]
    screenshot = data.get("screenshot")

    # Display Screenshot
    if screenshot and os.path.exists(screenshot):
        st.image(screenshot, caption="Chapter Screenshot", use_column_width=True)

    # Display All Text Versions
    file_map = {
        "📝 Original": str(base_path) + ".txt",
        "✍️ Rewritten": str(base_path) + "_rewritten.txt",
        "🔍 Reviewed": str(base_path) + "_reviewed.txt",
        "✅ Final": str(base_path) + "_final.txt"
    }

    st.subheader("📄 Text Versions")
    for label, path in file_map.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                st.markdown(f"**{label}**")
                st.text_area(label, f.read(), height=300, key=label)
        except FileNotFoundError:
            st.error(f"{label} file not found: {path}")

    # PDF Preview & Download
    if os.path.exists(pdf_file):
        st.subheader("📕 PDF Preview & Download")
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name=os.path.basename(pdf_file),
                mime="application/pdf"
            )
        st.components.v1.html(
            f"""<iframe src="file://{os.path.abspath(pdf_file)}" width="100%" height="600"></iframe>""",
            height=600,
        )

    # Audio Playback
    if os.path.exists(audio_file):
        st.subheader("🔊 Audio Narration")
        st.audio(audio_file, format="audio/mp3")
        with open(audio_file, "rb") as f:
            st.download_button(
                label="📥 Download MP3",
                data=f,
                file_name=os.path.basename(audio_file),
                mime="audio/mpeg"
            )

# === UI Logic ===
mode = st.radio("Choose Mode:", ["🔁 Fully Agentic (Auto)", "👤 Human-in-the-loop (Manual Review)"])

with st.form("chapter_form"):
    url = st.text_input("Enter Chapter URL (e.g., Wikisource):")
    feedback_score = st.slider("Rate the last output (feedback)", 1, 5, 5)
    submitted = st.form_submit_button("🚀 Start Processing")

# ========== FULLY AUTOMATED MODE ==========
if submitted and mode == "🔁 Fully Agentic (Auto)":
    if not url:
        st.warning("⚠️ Please enter a valid URL.")
    else:
        with st.spinner("🤖 Running full agentic pipeline..."):
            try:
                response = requests.post(f"{BASE_API}/process-agentic/", json={
                    "url": url,
                    "feedback_score": feedback_score
                })
                if response.status_code == 200:
                    data = response.json()
                    chapter_id = data["chapter_id"]
                    show_output(data, chapter_id)
                else:
                    st.error(f"❌ API error: {response.status_code}")
            except Exception as e:
                st.exception(e)

# ========== HUMAN-IN-THE-LOOP MODE ==========
elif submitted and mode == "👤 Human-in-the-loop (Manual Review)":
    if not url:
        st.warning("⚠️ Please enter a valid URL.")
    else:
        with st.spinner("📥 Scraping & Rewriting..."):
            try:
                response = requests.post(f"{BASE_API}/agentic/rewrite/", json={"url": url})
                if response.status_code == 200:
                    result = response.json()
                    chapter_id = result["chapter_id"]
                    rewritten_text = result["rewritten_text"]
                    screenshot = result.get("screenshot")

                    st.success("✅ Rewriting complete! Please edit and approve below:")

                    if screenshot and os.path.exists(screenshot):
                        st.image(screenshot, caption="Screenshot during scrape", use_column_width=True)

                    edited_text = st.text_area("✍️ Edit Rewritten Text", rewritten_text, height=500)
                    approve_btn = st.button("✅ Approve & Finalize")

                    if approve_btn:
                        with st.spinner("🔁 Sending for review, edit, PDF/audio..."):
                            approval = requests.post(f"{BASE_API}/agentic/approve/", json={
                                "chapter_id": chapter_id,
                                "final_text": edited_text,
                                "feedback_score": feedback_score
                            })
                            if approval.status_code == 200:
                                final_data = approval.json()
                                st.success("✅ Final output generated after review!")

                                pdf_file = final_data.get("pdf_file")
                                audio_file = final_data.get("audio_file")

                                if pdf_file and os.path.exists(pdf_file):
                                    st.subheader("📕 Final PDF")
                                    with open(pdf_file, "rb") as f:
                                        st.download_button("📥 Download PDF", f, file_name=os.path.basename(pdf_file))
                                        st.components.v1.html(
                                            f"""<iframe src="file://{os.path.abspath(pdf_file)}" width="100%" height="600"></iframe>""",
                                            height=600,
                                        )

                                if audio_file and os.path.exists(audio_file):
                                    st.subheader("🔊 Audio Narration")
                                    st.audio(audio_file)
                                    with open(audio_file, "rb") as f:
                                        st.download_button("📥 Download MP3", f, file_name=os.path.basename(audio_file))
                            else:
                                st.error(f"❌ Approval failed: {approval.text}")
                else:
                    st.error(f"❌ Rewrite API failed: {response.text}")
            except Exception as e:
                st.exception(e)
