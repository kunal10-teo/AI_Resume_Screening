from ai_matcher import semantic_similarity
from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import joblib
from pypdf import PdfReader
import re
import sys
import os



# ============================================================
# ROOT DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(BASE_DIR)

# ============================================================
# PROJECT IMPORTS
# ============================================================

from pdf_report import create_report
from ranking import rank_candidates
from database import save_candidate, get_candidates

# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = "resume_screening_secret"

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# ============================================================
# MODEL
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "resume_model.pkl"
)

try:
    model = joblib.load(MODEL_PATH)
    print("ML model loaded successfully.")
except Exception as e:
    model = None
    print("Warning: Model could not be loaded:", e)


# ============================================================
# SKILLS DATABASE
# ============================================================

skills_list = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "artificial intelligence",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "keras",
    "pytorch",
    "matplotlib",
    "seaborn",
    "flask",
    "django",
    "fastapi",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "gcp",
    "power bi",
    "tableau",
    "excel",
    "nlp",
    "natural language processing",
    "computer vision",
    "spark",
    "hadoop"
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    text = text.lower()

    text = re.sub(
        r"[/|,;:()\[\]{}]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    text = normalize_text(text)

    found_skills = []

    for skill in skills_list:

        skill_normalized = normalize_text(skill)

        pattern = (
            r"(?<!\w)"
            + re.escape(skill_normalized)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):

    text = text.lower()

    experience_values = []

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)\s+(?:of\s+)?experience",
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        for value in matches:

            try:
                experience_values.append(
                    float(value)
                )
            except ValueError:
                pass

    if experience_values:
        return max(experience_values)

    return 0


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def calculate_similarity(resume, job):

    return semantic_similarity(
        resume,
        job
    )


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    resume_text,
    job_description,
    resume_skills,
    job_skills
):

    if job_skills:

        matched_skills = [
            skill
            for skill in job_skills
            if skill in resume_skills
        ]

        skill_score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

    else:

        matched_skills = []
        skill_score = 0

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    if job_skills:

        final_score = (
            skill_score * 0.60
            +
            similarity_score * 0.40
        )

    else:

        final_score = similarity_score

    final_score = min(
        max(final_score, 0),
        100
    )

    return round(
        final_score,
        2
    ), matched_skills


# ============================================================
# CANDIDATE STATUS
# ============================================================

def calculate_selection(
    score,
    experience
):

    if score >= 80:
        return "Strong Candidate"

    elif score >= 65:
        return "Shortlisted"

    elif score >= 50:
        return "Review Required"

    else:
        return "Rejected"

# ============================================================
# HOME PAGE
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    result = ""
    skills_found = []
    missing_skills = []
    matched_skills = []

    score = 0
    similarity_score = 0
    skill_score = 0

    experience = 0
    selection = ""

    name = ""

    if request.method == "POST":

        # ----------------------------------------------------
        # Candidate Name
        # ----------------------------------------------------

        name = request.form.get(
            "name",
            "Unknown"
        ).strip()

        if not name:
            name = "Unknown"

        # ----------------------------------------------------
        # Resume File
        # ----------------------------------------------------

        file = request.files.get(
            "resume"
        )

        if not file or file.filename == "":
            return "Please upload a PDF resume."

        # ----------------------------------------------------
        # Job Description
        # ----------------------------------------------------

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        if not job_description:
            return "Please enter a job description."

        # ----------------------------------------------------
        # PDF Parsing
        # ----------------------------------------------------

        try:

            reader = PdfReader(file)

            resume_text = ""

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    resume_text += " " + text

            resume_text = normalize_text(
                resume_text
            )

        except Exception as e:

            return f"Could not read resume PDF: {e}"

        if not resume_text:

            return "Could not extract text from the resume."

        # ----------------------------------------------------
        # Resume Skills
        # ----------------------------------------------------

        skills_found = extract_skills(
            resume_text
        )

        # ----------------------------------------------------
        # Job Skills
        # ----------------------------------------------------

        job_description_normalized = normalize_text(
            job_description
        )

        job_skills = extract_skills(
            job_description_normalized
        )

        # ----------------------------------------------------
        # Missing Skills
        # ----------------------------------------------------

        missing_skills = [
            skill
            for skill in job_skills
            if skill not in skills_found
        ]

        # ----------------------------------------------------
        # Matched Skills
        # ----------------------------------------------------

        matched_skills = [
            skill
            for skill in job_skills
            if skill in skills_found
        ]

        # ----------------------------------------------------
        # Similarity
        # ----------------------------------------------------

        similarity_score = calculate_similarity(
            resume_text,
            job_description_normalized
        )

        # ----------------------------------------------------
        # Skill Score
        # ----------------------------------------------------

        if job_skills:

            skill_score = round(
                (
                    len(matched_skills)
                    /
                    len(job_skills)
                ) * 100,
                2
            )

        else:

            skill_score = 0

        # ----------------------------------------------------
        # ATS Score
        # ----------------------------------------------------

        score, matched_skills = calculate_ats_score(
            resume_text,
            job_description_normalized,
            skills_found,
            job_skills
        )

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience = extract_experience(
            resume_text
        )

        # ----------------------------------------------------
        # ML Job Role Prediction
        # ----------------------------------------------------

        if model is not None:

            try:

                prediction = model.predict(
                    [resume_text]
                )

                result = str(
                    prediction[0]
                )

            except Exception as e:

                print(
                    "Prediction error:",
                    e
                )

                result = "Unknown"

        else:

            result = "Unknown"

        # ----------------------------------------------------
        # Candidate Selection
        # ----------------------------------------------------

        selection = calculate_selection(
            score,
            experience
        )

        # ----------------------------------------------------
        # Save Candidate
        # ----------------------------------------------------

        try:

            save_candidate(
                name,
                result,
                score,
                experience,
                selection
            )

        except Exception as e:

            print(
                "Database error:",
                e
            )

        # ----------------------------------------------------
        # Console Information
        # ----------------------------------------------------

        print(
            "\n=============================="
        )

        print(
            "AI RESUME SCREENING RESULT"
        )

        print(
            "=============================="
        )

        print(
            "Name:",
            name
        )

        print(
            "Predicted Role:",
            result
        )

        print(
            "ATS Score:",
            score
        )

        print(
            "Similarity:",
            similarity_score
        )

        print(
            "Skill Score:",
            skill_score
        )

        print(
            "Experience:",
            experience
        )

        print(
            "Matched Skills:",
            matched_skills
        )

        print(
            "Missing Skills:",
            missing_skills
        )

        print(
            "Status:",
            selection
        )

        print(
            "==============================\n"
        )

    return render_template(
        "index.html",
        result=result,
        skills=skills_found,
        matched=matched_skills,
        missing=missing_skills,
        score=score,
        similarity_score=similarity_score,
        skill_score=skill_score,
        experience=experience,
        selection=selection,
        name=name
    )
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    candidates = get_candidates()

    return render_template(
        "dashboard.html",
        candidates=candidates
    )

# ============================================================
# LOGIN
# ============================================================
@app.route("/bulk_upload", methods=["GET", "POST"])
def bulk_upload():

    if "admin" not in session:
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":

        files = request.files.getlist("resumes")
        job_description = request.form.get("job_description", "").lower()

        if not job_description:
            return "Job description is required."

        for file in files:

            if not file or file.filename == "":
                continue

            if not file.filename.lower().endswith(".pdf"):
                continue

            try:

                reader = PdfReader(file)

                resume_text = ""

                for page in reader.pages:
                    text = page.extract_text()

                    if text:
                        resume_text += text.lower() + " "

                prediction = model.predict([resume_text])
                role = prediction[0]

                score = calculate_match(
                    resume_text,
                    job_description
                )

                experience = extract_experience(
                    resume_text
                )

                skills_found = []

                for skill in skills_list:
                    if skill in resume_text:
                        skills_found.append(skill)

                missing_skills = []

                for skill in required_skills:
                    if skill not in skills_found:
                        missing_skills.append(skill)

                if score >= 70 and experience >= 1:
                    status = "Selected"
                else:
                    status = "Rejected"

                candidate_name = os.path.splitext(
                    secure_filename(file.filename)
                )[0]

                save_candidate(
                    candidate_name,
                    role,
                    score,
                    experience,
                    status
                )

                results.append({
                    "name": candidate_name,
                    "role": role,
                    "score": score,
                    "experience": experience,
                    "skills": skills_found,
                    "missing": missing_skills,
                    "status": status
                })

            except Exception as e:

                results.append({
                    "name": file.filename,
                    "role": "Error",
                    "score": 0,
                    "experience": 0,
                    "skills": [],
                    "missing": [],
                    "status": str(e)
                })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        for index, candidate in enumerate(
            results,
            start=1
        ):
            candidate["rank"] = index

    return render_template(
        "bulk_upload.html",
        results=results
    )
# ============================================================
# GENERATE REPORT
# ============================================================

@app.route(
    "/generate_report/<int:id>"
)
def generate_report(id):

    if "admin" not in session:

        return redirect(
            url_for("login")
        )

    candidates = get_candidates()

    candidate = None

    for c in candidates:

        if c[0] == id:

            candidate = c

            break

    if candidate is None:

        return "Candidate not found"

    file = create_report(
        candidate[1],
        candidate[2],
        candidate[3],
        candidate[4],
        [
            "Python",
            "SQL",
            "Machine Learning"
        ],
        [
            "AWS"
        ],
        candidate[5]
    )

    return f"Report Generated: {file}"


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )


