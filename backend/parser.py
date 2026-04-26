import re
import pdfplumber
from utils import clean_text, normalize_skill, TECH_SKILLS, SYNONYM_MAP

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    print("Warning: spacy or 'en_core_web_sm' model not found. Using basic matching.")
    nlp = None

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
    if not text:
        return []
    
    found_skills = set()
    cleaned = clean_text(text)
    
    all_known_skills = TECH_SKILLS.get("critical", []) + TECH_SKILLS.get("optional", []) + list(SYNONYM_MAP.keys())
    
    for skill in all_known_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, cleaned):
            found_skills.add(normalize_skill(skill))
            
    if nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                ent_norm = normalize_skill(ent.text)
                if ent_norm in all_known_skills:
                    found_skills.add(ent_norm)
            for chunk in doc.noun_chunks:
                chunk_norm = normalize_skill(chunk.text)
                if chunk_norm in all_known_skills:
                    found_skills.add(chunk_norm)
        except Exception as e:
            print(f"Spacy extraction error: {e}")

    return list(found_skills) if found_skills else []

def preprocess_for_tfidf(text: str) -> str:
    if not text:
        return ""
    cleaned = clean_text(text)
    if not nlp:
        return cleaned
    
    try:
        doc = nlp(cleaned)
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.text.strip()]
        return " ".join(tokens)
    except Exception as e:
        print(f"Spacy preprocess error: {e}")
        return cleaned