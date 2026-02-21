import spacy
from sentence_transformers import SentenceTransformer

SHORTLIST_THRESHOLD = 65

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")