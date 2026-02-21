def calculate_weighted_match(resume_skills, must_have, good_to_have):
    must_matched = set(resume_skills) & set(must_have)
    good_matched = set(resume_skills) & set(good_to_have)

    if not must_have:
        return 0, []

    must_score = (len(must_matched) / len(must_have)) * 70
    good_score = (len(good_matched) / len(good_to_have)) * 30 if good_to_have else 0

    total_score = must_score + good_score
    matched = list(must_matched) + list(good_matched)

    return round(total_score, 2), matched

def calculate_final_resume_score(skill_score, semantic_score):
    return round((skill_score * 0.7) + (semantic_score * 0.3), 2)

def calculate_skill_match(resume_skills, jd_skills):
    matched = set(resume_skills) & set(jd_skills)

    if not jd_skills:
        return 0, []

    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2), list(matched)