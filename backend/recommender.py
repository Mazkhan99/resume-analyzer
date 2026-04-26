import re

def generate_suggestions(missing_skills: list, critical_missing: list) -> list:
    suggestions = []
    
    # 1. Skill-based suggestions
    if critical_missing:
        top_critical = critical_missing[:3]
        skills_str = ", ".join(top_critical).title()
        suggestions.append(f"Master critical missing skills: {skills_str}. Build a small project demonstrating these to stand out.")
        
    if missing_skills:
        tools = [s for s in missing_skills if s in ["git", "docker", "kubernetes", "aws", "azure", "jira", "jenkins", "ci/cd"]]
        if tools:
            suggestions.append(f"Learn essential tools like {', '.join(tools[:2]).title()}. These are often quick to pick up via crash courses.")
        elif len(missing_skills) > len(critical_missing):
             suggestions.append(f"Consider familiarizing yourself with secondary requirements like '{missing_skills[0].title()}'.")
             
    # 2 & 3. Resume improvement & ATS optimization (if no skills missing, or as general advice)
    if not missing_skills and not critical_missing:
        suggestions.append("Your technical skill match is excellent. Focus on describing the business impact of these skills.")
        suggestions.append("Ensure your resume uses standard ATS-friendly formatting (no complex tables or graphics).")
        suggestions.append("Tailor your summary section to explicitly mention the role title you are applying for.")
    else:
        suggestions.append("Review the job description carefully and ensure your resume keywords exactly match their terminology to pass ATS filters.")

    return suggestions if suggestions else []

def analyze_resume_quality(resume_text: str) -> dict:
    issues = []
    recommendations = []
    text_lower = (resume_text or "").lower()
    
    has_numbers = bool(re.search(r'\d+%|\d+\s*(?:million|billion|k|m)|increased by|decreased by', text_lower))
    if not has_numbers:
        issues.append("Lack of quantified achievements.")
        recommendations.append("Add measurable impact: 'Accomplished [X] as measured by [Y], by doing [Z]'.")

    action_verbs = ["developed", "created", "led", "managed", "designed", "implemented", "optimized", "architected"]
    verbs_found = [v for v in action_verbs if v in text_lower]
    if len(verbs_found) < 3:
        issues.append("Weak action verbs.")
        recommendations.append(f"Start bullet points with strong verbs like: {', '.join(action_verbs[:3]).title()}.")

    if "project" not in text_lower and "portfolio" not in text_lower:
         issues.append("Missing projects section.")
         recommendations.append("Include a 'Projects' section to demonstrate practical experience.")

    if not issues:
         recommendations.append("Resume structure is strong. Continue using clear metrics and action verbs.")
         
    return {
        "issues": issues if issues else [],
        "recommendations": recommendations if recommendations else []
    }
