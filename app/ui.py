import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from main import generate_resume
from utils_helper import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_keywords,
    match_keywords,
    calculate_score,
    calculate_ats_score
)


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


st.set_page_config(page_title="AI Job Assistant", layout="wide")

st.write("✅ App is loading...")

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
    uploaded_file = st.file_uploader(
        "📎 Upload Resume (PDF or Word)",
        type=["pdf", "docx"]
    )

    resume = ""

    if uploaded_file is not None:
        file_type = uploaded_file.type

        if file_type == "application/pdf":
            resume = extract_text_from_pdf(uploaded_file)

        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume = extract_text_from_docx(uploaded_file)

        st.success("Resume uploaded successfully!")

    st.divider()

    resume_text = st.text_area("Or paste your resume here", height=200)

    if uploaded_file is not None:
        final_resume = resume
    elif resume_text.strip() != "":
        final_resume = resume_text
    else:
        final_resume = ""

if uploaded_file is not None and resume_text.strip():
    st.info("Both uploaded file and pasted text detected. Using uploaded resume.")

# ----------- BUTTON -----------
generate = st.button("✨ Generate Tailored Resume", use_container_width=True)

# ----------- LOGIC -----------
if generate:
    if not jd.strip():
        st.warning("⚠️ Please enter Job Description")

    elif final_resume.strip() == "":
        st.warning("⚠️ Please upload or paste resume")

    else:
        jd_keywords = extract_keywords(jd)
        resume_keywords = extract_keywords(final_resume)

        matched, missing = match_keywords(jd_keywords, resume_keywords)
        score = calculate_score(jd_keywords, matched)
        ats_score = calculate_ats_score(jd, final_resume, matched)

        # ----------- SCORE SECTION -----------
        st.subheader("📊 Match Analysis")

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        metric_col1.metric("🎯 Keyword Score", f"{score}%")
        metric_col2.metric("✅ Matched Skills", len(matched))
        metric_col3.metric("❌ Missing Skills", len(missing))
        metric_col4.metric("🤖 ATS Score", f"{ats_score}%")

        # ----------- ATS FEEDBACK -----------
        if ats_score >= 80:
            st.success("🔥 Strong ATS match! Your resume looks well aligned with the job description.")
        elif ats_score >= 60:
            st.warning("⚡ Decent ATS match. You can improve it by adding more relevant keywords and sections.")
        else:
            st.error("🚨 Low ATS match. Your resume needs more alignment with the job description.")

        st.markdown("### 🧠 Skills Breakdown")

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:
            st.markdown("**✅ Matched Skills**")
            st.write(", ".join(matched[:15]) if matched else "None")

        with skill_col2:
            st.markdown("**❌ Missing Skills**")
            st.write(", ".join(missing[:15]) if missing else "None")

        # ----------- IMPROVEMENT TIPS -----------
        st.markdown("### 📈 Suggestions to Improve ATS Score")

        suggestions = []

        if missing:
            suggestions.append(f"Add missing keywords where relevant: {', '.join(missing[:10])}")

        if "skills" not in final_resume.lower():
            suggestions.append("Add a dedicated Skills section.")

        if "experience" not in final_resume.lower():
            suggestions.append("Add or clearly label your Experience section.")

        if "education" not in final_resume.lower():
            suggestions.append("Add or clearly label your Education section.")

        word_count = len(final_resume.split())
        if word_count < 300:
            suggestions.append("Your resume looks short. Add more relevant experience, projects, or achievements.")
        elif word_count > 1200:
            suggestions.append("Your resume may be too long. Try making it more concise and targeted.")

        if suggestions:
            for tip in suggestions:
                st.write(f"- {tip}")
        else:
            st.write("- Your resume already has a solid ATS-friendly structure.")

        st.divider()

        # ----------- AI OUTPUT -----------
        with st.spinner("✨ Generating premium resume..."):
            output = generate_resume(jd, final_resume, missing)

        st.subheader("📄 Tailored Resume")
        st.code(output, language="markdown")

        # ----------- DOWNLOAD BUTTON -----------
        pdf = create_pdf(output)

        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf,
            file_name="tailored_resume.pdf",
            mime="application/pdf"
        )