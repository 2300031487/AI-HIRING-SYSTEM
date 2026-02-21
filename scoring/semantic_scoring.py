from sklearn.metrics.pairwise import cosine_similarity
from config import model

def semantic_match_score(resume_text, jd_text):
    embeddings = model.encode([resume_text, jd_text])
    similarity = cosine_similarity(
        [embeddings[0]], 
        [embeddings[1]]
    )[0][0]

    return round(similarity * 100, 2)