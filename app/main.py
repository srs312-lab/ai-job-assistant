import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from utils_helper import extract_keywords, match_keywords

# Load local env (for local dev)
load_dotenv()

# Get API key (local OR Streamlit Cloud)
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Safety check (VERY important)
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Add it to .env or Streamlit secrets.")

# Initialize client
client = OpenAI(api_key=api_key)

def main():
    print("🚀 AI Job Assistant Started")

    jd = multi_line_input("\nPaste Job Description:")
    resume = multi_line_input("\nPaste Resume:")

    print("\n🔍 Analyzing...")

    jd_keywords = extract_keywords(jd)
    resume_keywords = extract_keywords(resume)

    matched, missing = match_keywords(jd_keywords, resume_keywords)

    print("\n✅ Matching Skills:", matched[:10])
    print("❌ Missing Skills:", missing[:10])

    print("\n⏳ Generating tailored resume...\n")

    output = generate_resume(jd, resume)

    print("\n📄 Tailored Resume:\n")
    print(output)

def multi_line_input(prompt):
    print(prompt)
    print("(Paste text. Press ENTER, then type 'END' on a new line and press ENTER)\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines)

def generate_resume(jd, resume, missing_skills):
    prompt = f"""
You are a professional resume writer and ATS expert.

Rewrite the resume tailored to the job description.

STRICT FORMAT:

NAME
Email | Phone | LinkedIn

SUMMARY
2-3 lines aligned with the role

SKILLS
List relevant technical and business skills

EXPERIENCE
For each role:
- Role | Company | Dates
- 3–5 bullet points
- Use strong action verbs
- Include measurable impact (%, $, time saved)

PROJECTS (if applicable)
- Highlight relevant work

EDUCATION
- Degree | University

IMPORTANT RULES:
- Prioritize relevance to job description
- Incorporate these missing skills if possible: {missing_skills}
- Do NOT invent fake experience
- Improve wording, clarity, and impact
- Keep it concise and professional

JOB DESCRIPTION:
{jd}

CURRENT RESUME:
{resume}

Return ONLY the formatted resume.
"""
    prompt = f"""
You are an expert resume writer.

Rewrite the resume to match the job description.

IMPORTANT:
- Emphasize relevant experience
- Add measurable impact
- Include these missing skills if applicable: {missing_skills}
- Keep it ATS-friendly and structured

Job Description:
{jd}

Candidate Resume:
{resume}

Return a clean, professional resume.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional resume assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def main():
    print("🚀 AI Job Assistant Started")

    jd = input("\nPaste Job Description:\n")
    resume = input("\nPaste Resume:\n")

    print("\n⏳ Generating tailored resume...\n")

    output = generate_resume(jd, resume)

    print("\n✅ Tailored Resume:\n")
    print(output)


if __name__ == "__main__":
    main()