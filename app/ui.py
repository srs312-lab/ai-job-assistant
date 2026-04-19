from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 8))

    doc.build(content)
    buffer.seek(0)
    return buffer
import streamlit as st
from main import generate_resume
from utils import extract_keywords, match_keywords, calculate_score

st.set_page_config(page_title="AI Job Assistant", layout="wide")

# ----------- HEADER -----------
st.markdown(
    """
    <h1 style='text-align: center;'>🚀 AI Job Assistant</h1>
    <p style='text-align: center; color: gray;'>
    Tailor your resume intelligently using AI
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ----------- INPUT SECTION -----------
col1, col2 = st.columns(2)

with col1:
    jd = st.text_area("📄 Job Description", height=300)

with col2:
    resume = st.text_area("🧾 Your Resume", height=300)

st.divider()

# ----------- BUTTON -----------
generate = st.button("✨ Generate Tailored Resume", use_container_width=True)

# ----------- LOGIC -----------
if generate:
    if jd and resume:

        jd_keywords = extract_keywords(jd)
        resume_keywords = extract_keywords(resume)

        matched, missing = match_keywords(jd_keywords, resume_keywords)
        score = calculate_score(jd_keywords, matched)

        # ----------- SCORE CARD -----------
        st.subheader("📊 Match Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🎯 Score", f"{score}%")

        with col2:
            st.metric("✅ Matched", len(matched))

        with col3:
            st.metric("❌ Missing", len(missing))

        # ----------- SKILLS DISPLAY -----------
        st.markdown("### 🧠 Skills Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✅ Matched Skills**")
            st.write(", ".join(matched[:15]) if matched else "None")

        with col2:
            st.markdown("**❌ Missing Skills**")
            st.write(", ".join(missing[:15]) if missing else "None")

        st.divider()

        # ----------- AI OUTPUT -----------
        with st.spinner("✨ Generating premium resume..."):
            output = generate_resume(jd, resume, missing)

        st.subheader("📄 Tailored Resume")

        st.markdown("### 📄 Tailored Resume")
        st.markdown(f"```\n{output}\n```")

        # ----------- DOWNLOAD BUTTON -----------
        pdf = create_pdf(output)
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf,
            file_name="tailored_resume.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("⚠️ Please fill both fields")