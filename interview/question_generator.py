def generate_structured_interview(must_have, good_to_have):
    questions = []

    questions.append(("intro",
        "Please introduce yourself and describe your technical background."
    ))

    for skill in must_have:
        questions.append((skill,
            f"Describe a real-world project where you used {skill}."
        ))

    if good_to_have:
        optional = ", ".join(good_to_have)
        questions.append(("optional",
            f"You mentioned skills like {optional}. Can you describe your experience?"
        ))

    return questions