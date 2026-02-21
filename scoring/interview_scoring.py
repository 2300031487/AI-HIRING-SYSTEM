from sklearn.metrics.pairwise import cosine_similarity
from config import model
from textblob import TextBlob

from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def skill_alignment_score(skill, answer):
    embeddings = model.encode([skill, answer], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    score = float(similarity[0][0])
    return max(min(score * 100, 100), 0)

def semantic_relevance_score(question, answer):
    embeddings = model.encode([question, answer], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    score = float(similarity[0][0])
    return max(min(score * 100, 100), 0)

def depth_score(answer):
    words = len(answer.split())
    
    if words < 30:
        return 30
    elif words < 80:
        return 60
    elif words < 150:
        return 85
    else:
        return 100

def evaluate_answer_pro(question, skill, answer):
    
    semantic_score = semantic_relevance_score(question, answer)
    skill_score = skill_alignment_score(skill, answer)
    depth = depth_score(answer)

    final = (
        semantic_score * 0.4 +
        skill_score * 0.3 +
        depth * 0.2
    )

    return round(final, 2)

def analyze_sentiment(answer):
    polarity = TextBlob(answer).sentiment.polarity
    return round(((polarity + 1) / 2) * 100, 2)