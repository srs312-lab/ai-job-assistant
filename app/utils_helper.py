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
