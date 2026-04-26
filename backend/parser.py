import pdfplumber
from utils import clean_text, normalize_skill, TECH_SKILLS, SYNONYM_MAP

def extract_text_from_pdf(pdf_file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text


def extract_skills_from_text(text: str) -> list:
    """
    Extract skills using keyword matching only (FAST & STABLE)
    """
    found_skills = set()
    cleaned = clean_text(text)

    all_known_skills = TECH_SKILLS["critical"] + TECH_SKILLS["optional"] + list(SYNONYM_MAP.keys())

    import re
    for skill in all_known_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, cleaned):
            found_skills.add(normalize_skill(skill))

    return list(found_skills)


def preprocess_for_tfidf(text: str) -> str:
    """
    Simple preprocessing without NLP
    """
    return clean_text(text)