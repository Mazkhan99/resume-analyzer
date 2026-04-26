from parser import extract_skills_from_text
from utils import TECH_SKILLS

def analyze_gap(resume_text: str, jd_text: str) -> dict:
    resume_text = resume_text or ""
    jd_text = jd_text or ""
    
    resume_skills = set(extract_skills_from_text(resume_text))
    jd_skills = set(extract_skills_from_text(jd_text))
    
    missing_all = jd_skills - resume_skills
    
    critical_missing = set()
    standard_missing = set()
    
    critical_db = set(TECH_SKILLS.get("critical", []))
    
    for skill in missing_all:
        if skill in critical_db:
            critical_missing.add(skill)
        else:
            standard_missing.add(skill)
            
    return {
        "skills_found": list(resume_skills) if resume_skills else [],
        "jd_skills": list(jd_skills) if jd_skills else [],
        "missing_skills": list(standard_missing) if standard_missing else [],
        "critical_missing_skills": list(critical_missing) if critical_missing else []
    }
