import json

def load_skills(file_path):
    with open(file_path, "r") as f:
        return [line.strip().lower() for line in f.readlines()]

import re

action_verbs = [
    "developed", "built", "implemented", "designed",
    "deployed", "optimized", "created", "engineered",
    "integrated", "maintained"
]

learning_words = [
    "studied", "coursework", "learned", "basic",
    "familiar with"
]

def extract_skills_context_aware(text, skills_list, nlp):

    doc = nlp(text)
    extracted = {}

    for sent in doc.sents:
        sentence_text = sent.text.lower()

        for skill in skills_list:
            escaped = re.escape(skill)
            pattern = r'(?<!\w)' + escaped + r'(?!\w)'

            if re.search(pattern, sentence_text):

                score = 1  # base score

                # Boost if action verbs present
                if any(verb in sentence_text for verb in action_verbs):
                    score += 2

                # Reduce if only learning context
                if any(word in sentence_text for word in learning_words):
                    score -= 0.5

                # Detect years of experience
                exp_match = re.search(r'(\d+)\+?\s*(years|yrs)', sentence_text)
                if exp_match:
                    years = int(exp_match.group(1))
                    score += min(years, 5)  # cap at 5

                extracted[skill] = max(score, 0)

    return extracted

import re

def extract_skills(text, skills_list):
    text = text.lower()
    extracted = []

    for skill in skills_list:
        escaped_skill = re.escape(skill)

        # If skill contains special characters like + or #
        if any(char in skill for char in ['+', '#', '.']):
            pattern = r'(?<!\w)' + escaped_skill + r'(?!\w)'
        else:
            pattern = r'\b' + escaped_skill + r'\b'

        if re.search(pattern, text):
            extracted.append(skill)

    return list(set(extracted))

def load_taxonomy(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def normalize_skills(skills, taxonomy):
    normalized = []

    for skill in skills:
        skill_lower = skill.lower()
        found = False

        for canonical, variations in taxonomy.items():
            if skill_lower in variations:
                normalized.append(canonical)
                found = True
                break

        if not found:
            normalized.append(skill_lower)

    return list(set(normalized))