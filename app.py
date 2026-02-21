# import os

# from config import SHORTLIST_THRESHOLD
# from resume_parser.pdf_utils import extract_text_from_pdf, clean_text
# from resume_parser.contact_extractor import extract_name, extract_email
# from resume_parser.skill_extractor import (
#     load_skills, extract_skills, load_taxonomy, normalize_skills
# )
# from jd_processing.jd_parser import (
#     extract_jd_skills, extract_weighted_jd_skills
# )
# from scoring.skill_scoring import (
#     calculate_weighted_match, calculate_final_resume_score
# )
# from scoring.semantic_scoring import semantic_match_score
# from interview.question_generator import generate_structured_interview
# from scoring.interview_scoring import evaluate_answer, analyze_sentiment


# def main():

#     base_dir = os.path.abspath(os.path.dirname(__file__))

#     resumes_folder = os.path.join(base_dir, "data", "resumes")
#     skills_master_path = os.path.join(base_dir, "data", "skills_master.txt")
#     taxonomy_path = os.path.join(base_dir, "data", "skill_taxonomy.json")
#     jd_path = os.path.join(base_dir, "data", "job_descriptions", "jd1.txt")

#     skills_list = load_skills(skills_master_path)
#     taxonomy = load_taxonomy(taxonomy_path)

#     with open(jd_path, "r") as f:
#         jd_text = f.read()

#     jd_skills = normalize_skills(
#         extract_jd_skills(jd_text, skills_list),
#         taxonomy
#     )

#     must_have, good_to_have = extract_weighted_jd_skills(jd_text)
#     must_have = normalize_skills(must_have, taxonomy)
#     good_to_have = normalize_skills(good_to_have, taxonomy)

#     print("\n==============================")
#     print("JD Skills:", jd_skills)
#     print("Must Have Skills:", must_have)
#     print("Good To Have Skills:", good_to_have)
#     print("==============================\n")

#     candidates = []

#     for file in os.listdir(resumes_folder):
#         if not file.endswith(".pdf"):
#             continue

#         pdf_path = os.path.join(resumes_folder, file)

#         raw_text = extract_text_from_pdf(pdf_path)
#         cleaned_text = clean_text(raw_text)

#         name = extract_name(raw_text)
#         email = extract_email(cleaned_text)

#         skills = normalize_skills(
#             extract_skills(cleaned_text, skills_list),
#             taxonomy
#         )

#         skill_score, _ = calculate_weighted_match(
#             skills, must_have, good_to_have
#         )

#         semantic_score = semantic_match_score(
#             " ".join(skills),
#             " ".join(jd_skills)
#         )

#         final_score = calculate_final_resume_score(
#             skill_score,
#             semantic_score
#         )
#         print("\n==============================")
#         print("Candidate:", name)
#         print("Extracted Skills:", skills)
#         print("Skill Score:", skill_score)
#         print("Semantic Score:", semantic_score)
#         print("Final Resume Score:", final_score)
#         print("==============================")
#         candidates.append({
#             "name": name,
#             "email": email,
#             "resume_score": final_score,
#             "raw_text": raw_text
#         })
    
#     candidates = sorted(candidates, key=lambda x: x["resume_score"], reverse=True)
#     shortlisted = [c for c in candidates if c["resume_score"] >= SHORTLIST_THRESHOLD]

#     print("\nShortlisted Candidates:")
#     for c in shortlisted:
#         print(c["name"], "→", c["resume_score"])

#     for candidate in shortlisted:
#         print("\nInterview for:", candidate["name"])

#         questions = generate_structured_interview(must_have, good_to_have)
#         total_score = 0

#         for skill, question in questions:
#             print("\n", question)
#             answer = input("Your Answer: ")

#             if skill == "intro":
#                 sentiment = analyze_sentiment(answer)
#                 combined = sentiment
#             else:
#                 tech = evaluate_answer(answer, skill)
#                 sentiment = analyze_sentiment(answer)
#                 combined = (tech * 0.8) + (sentiment * 0.2)

#             total_score += combined

#         final_interview_score = round(total_score / len(questions), 2)
#         print("Final Interview Score:", final_interview_score)


# if __name__ == "__main__":
#     main()

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

from config import SHORTLIST_THRESHOLD
from resume_parser.pdf_utils import extract_text_from_pdf, clean_text
from resume_parser.contact_extractor import extract_name, extract_email
from resume_parser.skill_extractor import (
    load_skills, extract_skills, load_taxonomy, normalize_skills
)
from jd_processing.jd_parser import extract_jd_skills
from scoring.skill_scoring import calculate_skill_match, calculate_final_resume_score
from scoring.semantic_scoring import semantic_match_score

from interview.question_generator import generate_structured_interview
from scoring.interview_scoring import evaluate_answer_pro

#ranked_candidates = []

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///candidates.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    resume_skills = db.Column(db.Text)
    jd_skills = db.Column(db.Text)
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    skill_score = db.Column(db.Float)
    semantic_score = db.Column(db.Float)
    final_score = db.Column(db.Float)
    shortlisted = db.Column(db.Boolean)
    interview_score = db.Column(db.Float)
    interview_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load static data once
base_dir = os.path.abspath(os.path.dirname(__file__))
skills_list = load_skills(os.path.join(base_dir, "data", "skills_master.txt"))
taxonomy = load_taxonomy(os.path.join(base_dir, "data", "skill_taxonomy.json"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    resume_files = request.files.getlist("resumes")
    jd_text = request.form["jd"]

    jd_skills = normalize_skills(
        extract_jd_skills(jd_text, skills_list),
        taxonomy
    )

    for resume_file in resume_files:

        if resume_file.filename == "":
            continue

        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume_file.save(resume_path)

        raw_text = extract_text_from_pdf(resume_path)
        cleaned_text = clean_text(raw_text)

        name = extract_name(raw_text)
        email = extract_email(cleaned_text)

        resume_skills = normalize_skills(
            extract_skills(cleaned_text, skills_list),
            taxonomy
        )

        skill_score, _ = calculate_skill_match(resume_skills, jd_skills)

        semantic_score = semantic_match_score(
            " ".join(resume_skills),
            " ".join(jd_skills)
        )

        final_score = calculate_final_resume_score(skill_score, semantic_score)

        shortlisted = final_score >= SHORTLIST_THRESHOLD

        # Remove old record if exists
        existing = Candidate.query.filter_by(email=email).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        # Create new record
        new_candidate = Candidate(
            name=name,
            email=email,
            resume_skills=json.dumps(resume_skills),
            jd_skills=json.dumps(jd_skills),
            matched_skills=json.dumps(list(set(resume_skills) & set(jd_skills))),
            missing_skills=json.dumps(list(set(jd_skills) - set(resume_skills))),
            skill_score=skill_score,
            semantic_score=semantic_score,
            final_score=final_score,
            shortlisted=shortlisted
        )

        db.session.add(new_candidate)

    db.session.commit()

    return redirect("/dashboard")

@app.route("/delete/<int:id>", methods=["POST"])
def delete_candidate(id):
    candidate = Candidate.query.get(id)

    if candidate:
        db.session.delete(candidate)
        db.session.commit()

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    candidates = Candidate.query.order_by(Candidate.final_score.desc()).all()
    return render_template("dashboard.html", candidates=candidates)

@app.route("/candidate/<email>")
def candidate_detail(email):

    candidate = Candidate.query.filter_by(email=email).first()

    if not candidate:
        return "Candidate not found"
    if candidate:
        candidate.resume_skills = json.loads(candidate.resume_skills)
        candidate.jd_skills = json.loads(candidate.jd_skills)
        candidate.matched_skills = json.loads(candidate.matched_skills)
        candidate.missing_skills = json.loads(candidate.missing_skills)

    return render_template("candidate_detail.html", candidate=candidate)

@app.route("/interview/<int:id>", methods=["GET", "POST"])
def interview(id):

    candidate = Candidate.query.get(id)

    if not candidate or not candidate.shortlisted:
        return "Interview not allowed"

    resume_skills = json.loads(candidate.resume_skills)
    jd_skills = json.loads(candidate.jd_skills)

    questions = generate_structured_interview(jd_skills, [])

    if request.method == "POST":

        total_score = 0
        answers = request.form

        for skill, question in questions:

            answer = answers.get(skill, "")

            if skill == "intro":
                sentiment = analyze_sentiment(answer)
                combined = sentiment
            else:
                tech = evaluate_answer_pro(question, skill, answer)
                sentiment = analyze_sentiment(answer)
                combined = (tech * 0.8) + (sentiment * 0.2)

            total_score += combined

        final_interview_score = round(total_score / len(questions), 2)

        candidate.interview_score = final_interview_score
        candidate.interview_completed = True
        db.session.commit()
        return redirect("/dashboard")

    return render_template(
        "interview.html",
        candidate=candidate,
        questions=questions
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)