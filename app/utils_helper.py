import re
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())

    common_words = {
        "with", "from", "that", "this", "have", "will",
        "your", "about", "looking", "candidate", "experience",
        "skills", "role", "team", "work", "years"
    }

    keywords = [w for w in words if w not in common_words]
    return list(set(keywords))

def match_keywords(jd_keywords, resume_keywords):
    jd_set = set(jd_keywords)
    resume_set = set(resume_keywords)

    matched = jd_set & resume_set
    missing = jd_set - resume_set

    return list(matched), list(missing)

def calculate_score(jd_keywords, matched):
    if not jd_keywords:
        return 0

    score = (len(matched) / len(jd_keywords)) * 100
    return round(score)

def calculate_ats_score(jd_text, resume_text, matched_keywords):
    jd_words = jd_text.split()
    resume_words = resume_text.split()

    # --- 1. Keyword Match (50%) ---
    keyword_score = (len(matched_keywords) / len(set(jd_words))) if jd_words else 0
    keyword_score *= 50

    # --- 2. Section Coverage (20%) ---
    sections = ["experience", "skills", "education", "projects"]
    section_hits = sum(1 for sec in sections if sec in resume_text.lower())
    section_score = (section_hits / len(sections)) * 20

    # --- 3. Keyword Density (15%) ---
    density = len(matched_keywords) / len(resume_words) if resume_words else 0
    density_score = min(density * 100, 15)  # cap at 15

    # --- 4. Length Quality (15%) ---
    word_count = len(resume_words)
    if 400 <= word_count <= 900:
        length_score = 15
    elif 250 <= word_count < 400 or 900 < word_count <= 1200:
        length_score = 10
    else:
        length_score = 5

    total_score = keyword_score + section_score + density_score + length_score

    return round(total_score)
