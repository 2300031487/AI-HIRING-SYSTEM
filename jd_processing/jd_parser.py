import re

import re

def extract_jd_skills(jd_text, skills_list):
    jd_text = jd_text.lower()
    required = []

    for skill in skills_list:
        escaped_skill = re.escape(skill)

        if any(char in skill for char in ['+', '#', '.']):
            pattern = r'(?<!\w)' + escaped_skill + r'(?!\w)'
        else:
            pattern = r'\b' + escaped_skill + r'\b'

        if re.search(pattern, jd_text):
            required.append(skill)

    return list(set(required))

def extract_weighted_jd_skills(jd_text):
    lines = jd_text.lower().split("\n")
    must_have = []
    good_to_have = []
    section = None

    for line in lines:
        line = line.strip()

        if "must have" in line:
            section = "must"
            continue
        elif "good to have" in line:
            section = "good"
            continue

        if not line:
            continue

        if section == "must":
            must_have.append(line)
        elif section == "good":
            good_to_have.append(line)

    return list(set(must_have)), list(set(good_to_have))