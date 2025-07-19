# streamlit_app.py

import streamlit as st
import requests
import os
from pathlib import Path

API_URL = "http://localhost:8000/process-agentic/"

st.set_page_config(page_title="📘 AI-Powered Book Chapter Processor", layout="wide")
st.title("📚 Automated Book Workflow")

with st.form("chapter_form"):
    url = st.text_input("Enter Chapter URL (e.g., Wikisource):")
    feedback_score = st.slider("Rate the last output (feedback)", 1, 5, 5)
    submitted = st.form_submit_button("Run Agentic Processing")

if submitted:
    if not url:
        st.warning("⚠️ Please enter a valid URL.")
    else:
        with st.spinner("🤖 Processing chapter via multi-agent AI pipeline..."):
            try:
                response = requests.post(API_URL, json={"url": url, "feedback_score": feedback_score})
                if response.status_code == 200:
                    data = response.json()

                    st.success("✅ Processing complete!")

                    final_file = Path(data["final_text_file"])
                    base_path = final_file.with_name(final_file.stem.replace("_final", ""))
                    pdf_file = data["pdf_file"]
                    audio_file = data["audio_file"]
                    screenshot = data.get("screenshot")

                    # Display Screenshot if available
                    if screenshot and os.path.exists(screenshot):
                        st.image(screenshot, caption="Chapter Screenshot", use_column_width=True)

                    # Display all versions
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

                    # PDF Preview and Download
                    if os.path.exists(pdf_file):
                        st.subheader("📕 PDF Preview & Download")
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="📥 Download PDF",
                                data=f,
                                file_name=os.path.basename(pdf_file),
                                mime="application/pdf"
                            )
                        st.markdown("---")
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

                else:
                    st.error(f"❌ API error {response.status_code}: {response.text}")
            except Exception as e:
                st.exception(f"Unexpected error: {e}")
