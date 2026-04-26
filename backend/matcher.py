from parser import extract_skills_from_text
from utils import TECH_SKILLS

def analyze_gap(resume_text: str, jd_text: str) -> dict:
    resume_skills = set(extract_skills_from_text(resume_text))
    jd_skills = set(extract_skills_from_text(jd_text))
    
    missing_all = list(jd_skills - resume_skills)
    
    critical_missing = []
    standard_missing = []
    
    for skill in missing_all:
        if skill in TECH_SKILLS["critical"]:
            critical_missing.append(skill)
        else:
            standard_missing.append(skill)
            
    return {
        "skills_found": list(resume_skills),
        "jd_skills": list(jd_skills),
        "missing_skills": standard_missing,
        "critical_missing_skills": critical_missing
    }
