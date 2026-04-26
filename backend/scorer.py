from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_text_similarity(resume_processed: str, jd_processed: str) -> float:
    if not resume_processed or not jd_processed:
        return 0.0
        
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_processed, jd_processed])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score = similarity * 100
        return round(score, 2) if score > 0 else 0.0
    except ValueError:
        return 0.0
    except Exception:
        return 0.0

def calculate_skill_score(resume_skills: list, jd_skills: list) -> float:
    if not jd_skills:
        return 100.0 if resume_skills else 0.0
        
    set_resume = set(resume_skills) if resume_skills else set()
    set_jd = set(jd_skills) if jd_skills else set()
    
    if not set_jd:
        return 0.0
        
    matches = set_resume.intersection(set_jd)
    score = (len(matches) / len(set_jd)) * 100
    
    return round(score, 2) if score > 0 else 0.0

def calculate_multi_dimensional_scores(resume_processed: str, jd_processed: str, resume_skills: list, jd_skills: list) -> dict:
    skill_score = calculate_skill_score(resume_skills, jd_skills)
    similarity_score = calculate_text_similarity(resume_processed, jd_processed)
    
    weight_skill = 0.60
    weight_similarity = 0.40
    final = (skill_score * weight_skill) + (similarity_score * weight_similarity)
        
    return {
        "skill_score": round(skill_score, 2) if skill_score else 0.0,
        "similarity_score": round(similarity_score, 2) if similarity_score else 0.0,
        "final_score": round(final, 2) if final else 0.0
    }
