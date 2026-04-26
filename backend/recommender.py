import re

def generate_suggestions(missing_skills: list, critical_missing: list) -> list:
    suggestions = []
    
    if critical_missing:
        top_critical = critical_missing[:3]
        skills_str = ", ".join(top_critical).title()
        suggestions.append(f"You are missing highly critical skills: {skills_str}. Consider building a project using these technologies.")
        
    if missing_skills:
        tools = [s for s in missing_skills if s in ["git", "docker", "kubernetes", "aws", "azure", "jira", "jenkins", "ci/cd"]]
        if tools:
            suggestions.append(f"Missing DevOps/Tooling skills like {', '.join(tools[:2]).title()}. These can often be learned quickly.")
            
        if len(missing_skills) > len(critical_missing):
             suggestions.append(f"Also consider familiarizing yourself with secondary requirements like '{missing_skills[0].title()}'.")
             
    if not missing_skills and not critical_missing:
        suggestions.append("Outstanding! You have all the core and secondary skills mentioned in the job description.")
        
    return suggestions

def analyze_resume_quality(resume_text: str) -> dict:
    issues = []
    recommendations = []
    text_lower = resume_text.lower()
    
    has_numbers = bool(re.search(r'\d+%|\d+\s*(?:million|billion|k|m)|increased by|decreased by', text_lower))
    if not has_numbers:
        issues.append("Lack of measurable achievements.")
        recommendations.append("Use the XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Add specific numbers and percentages.")

    action_verbs = ["developed", "created", "led", "managed", "designed", "implemented", "optimized", "architected"]
    verbs_found = [v for v in action_verbs if v in text_lower]
    if len(verbs_found) < 3:
        issues.append("Low density of strong action verbs.")
        recommendations.append(f"Start your bullet points with strong action verbs like: {', '.join(action_verbs[:3]).title()}.")

    if "project" not in text_lower and "portfolio" not in text_lower:
         issues.append("Missing 'Projects' or 'Portfolio' reference.")
         recommendations.append("Add a 'Personal Projects' section to demonstrate relevant skills.")

    if not issues:
        issues.append("None detected.")
        recommendations.append("Your resume phrasing and structure look solid.")

    return {
        "issues": issues,
        "recommendations": recommendations
    }
