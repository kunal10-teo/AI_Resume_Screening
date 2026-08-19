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
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# PROJECT IMPORTS
# ============================================================
from semantic_matcher import semantic_match

from pdf_report import create_report

from database import (
    save_candidate,
    get_candidates
)

from ranking import (
    calculate_final_ranking_score,
    get_candidate_rank
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=os.path.join(
        BASE_DIR,
        "templates"
    )
)

app.secret_key = "resume_screening_secret"

app.config["MAX_CONTENT_LENGTH"] = (
    16 * 1024 * 1024
)


# ============================================================
# ML MODEL
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "resume_model.pkl"
)


try:

    model = joblib.load(
        MODEL_PATH
    )

    print(
        "ML model loaded successfully."
    )

except Exception as e:

    model = None

    print(
        "Warning: Model could not be loaded:",
        e
    )


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

    text = str(
        text or ""
    ).lower()

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

    text = normalize_text(
        text
    )

    found_skills = []

    for skill in skills_list:

        skill_normalized = normalize_text(
            skill
        )

        pattern = (
            r"(?<!\w)"
            + re.escape(skill_normalized)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text
        ):
            found_skills.append(
                skill
            )

    return sorted(
        set(found_skills)
    )


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):

    text = str(
        text or ""
    ).lower()

    experience_values = []

    patterns = [

        r"(\d+(?:\.\d+)?)\s*"
        r"(?:year|years|yr|yrs)"
        r"\s+(?:of\s+)?experience",

        r"(\d+(?:\.\d+)?)\s*"
        r"(?:year|years|yr|yrs)"
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

        return max(
            experience_values
        )

    return 0


# ============================================================
# SEMANTIC AI MATCHING
# ============================================================

def calculate_similarity(
    resume,
    job
):

    try:

        score = semantic_match(
            resume,
            job
        )

        return round(
            min(
                max(
                    float(score),
                    0
                ),
                100
            ),
            2
        )

    except Exception as e:

        print(
            "Semantic matching error:",
            e
        )

        return 0.0


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    resume_text,
    job_description,
    resume_skills,
    job_skills
):

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

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

        # 60% Skill Match
        # 40% Semantic Match

        final_score = (

            skill_score * 0.60
            +
            similarity_score * 0.40

        )

    else:

        matched_skills = []

        skill_score = 0

        final_score = (
            similarity_score
        )

    final_score = min(
        max(
            final_score,
            0
        ),
        100
    )

    return (

        round(
            final_score,
            2
        ),

        matched_skills,

        round(
            similarity_score,
            2
        ),

        round(
            skill_score,
            2
        )
    )


# ============================================================
# CANDIDATE STATUS
# ============================================================

def calculate_selection(
    score,
    experience=0
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
# PREDICT JOB ROLE
# ============================================================

def predict_role(
    resume_text
):

    if model is None:

        return "Unknown"

    try:

        prediction = model.predict(
            [resume_text]
        )

        return str(
            prediction[0]
        )

    except Exception as e:

        print(
            "Prediction error:",
            e
        )

        return "Unknown"


# ============================================================
# PROJECT SCORE
# ============================================================

def calculate_project_score(
    resume_text
):

    project_keywords = [

        "project",
        "deployment",
        "github",
        "flask",
        "machine learning",
        "data science",
        "nlp",
        "api"

    ]

    project_matches = sum(

        1
        for keyword in project_keywords
        if keyword in resume_text

    )

    if not project_keywords:

        return 0

    project_score = (

        project_matches
        / len(project_keywords)

    ) * 100

    return min(
        project_score,
        100
    )


# ============================================================
# FINAL RANKING
# ============================================================

def calculate_ranking(
    skill_score,
    semantic_score,
    experience,
    project_score
):

    try:

        ranking_score = (
            calculate_final_ranking_score(
                skill_score,
                semantic_score,
                experience,
                project_score
            )
        )

        ranking_status = (
            get_candidate_rank(
                ranking_score
            )
        )

        return (
            round(
                float(ranking_score),
                2
            ),
            ranking_status
        )

    except Exception as e:

        print(
            "Ranking error:",
            e
        )

        return (
            0,
            "Unknown"
        )


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

    ranking_score = 0

    ranking_status = ""

    project_score = 0

    name = ""

    if request.method == "POST":

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        name = request.form.get(
            "name",
            "Unknown"
        ).strip()

        if not name:

            name = "Unknown"


        # ----------------------------------------------------
        # RESUME FILE
        # ----------------------------------------------------

        file = request.files.get(
            "resume"
        )

        if (
            not file
            or file.filename == ""
        ):

            return (
                "Please upload a PDF resume."
            )

        if not file.filename.lower().endswith(
            ".pdf"
        ):

            return (
                "Only PDF resumes are supported."
            )

        # ----------------------------------------------------
        # JOB DESCRIPTION
        # ----------------------------------------------------

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        if not job_description:

            return (
                "Please enter a job description."
            )

        job_description_normalized = normalize_text(
            job_description
        )

        job_skills = extract_skills(
            job_description_normalized
        )

        print("================================")
        print("JOB DESCRIPTION:")
        print(job_description_normalized)

        print("JOB SKILLS:")
        print(job_skills)

        print("================================")


        # ----------------------------------------------------
        # PDF PARSING
        # ----------------------------------------------------

        try:

            reader = PdfReader(
                file
            )

            resume_text = ""

            for page in reader.pages:

                text = page.extract_text()

                if text:

                    resume_text += (
                        " " + text
                    )

            resume_text = normalize_text(
                resume_text
            )

        except Exception as e:

            return (
                f"Could not read resume PDF: {e}"
            )


        if not resume_text:

            return (
                "Could not extract text "
                "from the resume."
            )
        # ----------------------------------------------------
        # JOB SKILLS
        # ----------------------------------------------------

        job_description_normalized = (
            normalize_text(
                job_description
            )
        )

        job_skills = extract_skills(
            job_description_normalized
        )


        # ----------------------------------------------------
        # RESUME SKILLS
        # ----------------------------------------------------

        skills_found = extract_skills(
            resume_text
        )


        matched_skills = [

            skill
            for skill in job_skills
            if skill in skills_found

        ]


        missing_skills = [

            skill
            for skill in job_skills
            if skill not in skills_found

        ]


        # ----------------------------------------------------
        # ATS + SEMANTIC SCORE
        # ----------------------------------------------------

        (
            score,
            matched_skills,
            similarity_score,
            skill_score
        ) = calculate_ats_score(

            resume_text,

            job_description_normalized,

            skills_found,

            job_skills
        )


        # ----------------------------------------------------
        # EXPERIENCE
        # ----------------------------------------------------

        experience = extract_experience(
            resume_text
        )


        # ----------------------------------------------------
        # PROJECT SCORE
        # ----------------------------------------------------

        project_score = (
            calculate_project_score(
                resume_text
            )
        )


        # ----------------------------------------------------
        # FINAL RANKING
        # ----------------------------------------------------

        (
            ranking_score,
            ranking_status
        ) = calculate_ranking(

            skill_score,

            similarity_score,

            experience,

            project_score
        )


        # ----------------------------------------------------
        # ML ROLE PREDICTION
        # ----------------------------------------------------

        result = predict_role(
            resume_text
        )


        # ----------------------------------------------------
        # CANDIDATE SELECTION
        # ----------------------------------------------------

        selection = calculate_selection(
            score,
            experience
        )


        # ----------------------------------------------------
        # SAVE CANDIDATE
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
        # CONSOLE OUTPUT
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
            "Final ATS Score:",
            score
        )

        print(
            "Semantic Score:",
            similarity_score
        )

        print(
            "Skill Score:",
            skill_score
        )

        print(
            "Project Score:",
            project_score
        )

        print(
            "Ranking Score:",
            ranking_score
        )

        print(
            "Ranking Status:",
            ranking_status
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


    # --------------------------------------------------------
    # RENDER HOME PAGE
    # --------------------------------------------------------

    return render_template(

        "index.html",

        result=result,

        skills=skills_found,

        matched=matched_skills,

        missing=missing_skills,

        score=score,

        similarity_score=similarity_score,

        skill_score=skill_score,

        project_score=project_score,

        ranking_score=ranking_score,

        ranking_status=ranking_status,

        experience=experience,

        selection=selection,

        name=name

    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == "admin"
            and password == "12345"
        ):

            session["admin"] = True

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        return "Invalid Login"

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for(
            "login"
        )
    )
# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    candidates = get_candidates()

    clean_candidates = []

    for candidate in candidates:

        candidate = list(candidate)

        try:
            score = candidate[3]

            if isinstance(score, bytes):
                score = float(score.decode("utf-8"))
            else:
                score = float(score)

            candidate[3] = score

        except (ValueError, TypeError, AttributeError):
            candidate[3] = 0.0

        clean_candidates.append(tuple(candidate))

    # Role-wise count
    roles = {}

    for candidate in clean_candidates:
        role = candidate[2]

        if role in roles:
            roles[role] += 1
        else:
            roles[role] = 1

    return render_template(
        "dashboard.html",
        candidates=clean_candidates,
        roles=roles
    )
    # --------------------------------------------------------
    # ROLE DISTRIBUTION
    # --------------------------------------------------------

    roles = {}

    for candidate in candidates:

        try:

            role = candidate[1]

            if role:
                roles[role] = roles.get(role, 0) + 1

        except Exception:
            pass

    # --------------------------------------------------------
    # SELECTION ANALYTICS
    # --------------------------------------------------------

    selected = 0
    rejected = 0

    for candidate in candidates:

        try:

            status = str(
                candidate[5]
            ).lower()

            if (
                "strong" in status
                or "shortlisted" in status
                or "selected" in status
            ):
                selected += 1

            elif "rejected" in status:
                rejected += 1

        except Exception:
            pass

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render_template(
        "dashboard.html",
        candidates=candidates,
        roles=roles,
        selected=selected,
        rejected=rejected
    )

# ============================================================
# BULK RESUME UPLOAD
# ============================================================

@app.route(
    "/bulk_upload",
    methods=["GET", "POST"]
)
def bulk_upload():

    if "admin" not in session:
        return redirect(
            url_for("login")
        )

    results = []

    if request.method == "POST":

        files = request.files.getlist(
            "resumes"
        )

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        if not job_description:
            return "Job description is required."

        job_description_normalized = normalize_text(
            job_description
        )

        job_skills = extract_skills(
            job_description_normalized
        )

        for file in files:

            if not file or file.filename == "":
                continue

            if not file.filename.lower().endswith(".pdf"):
                continue

            try:

                # PDF TEXT
                reader = PdfReader(file)

                resume_text = ""

                for page in reader.pages:

                    text = page.extract_text()

                    if text:
                        resume_text += " " + text

                resume_text = normalize_text(
                    resume_text
                )

                if not resume_text:
                    raise ValueError(
                        "No readable text found in PDF."
                    )

                # ROLE
                role = predict_role(
                    resume_text
                )

                # SKILLS
                skills_found = extract_skills(
                    resume_text
                )

                matched_skills = [
                    skill
                    for skill in job_skills
                    if skill in skills_found
                ]

                missing_skills = [
                    skill
                    for skill in job_skills
                    if skill not in skills_found
                ]

                # ATS SCORE
                (
                    final_score,
                    matched_skills,
                    semantic_score,
                    skill_score
                ) = calculate_ats_score(
                    resume_text,
                    job_description_normalized,
                    skills_found,
                    job_skills
                )

                # EXPERIENCE
                experience = extract_experience(
                    resume_text
                )

                # PROJECT SCORE
                project_score = calculate_project_score(
                    resume_text
                )

                # RANKING
                (
                    ranking_score,
                    ranking_status
                ) = calculate_ranking(
                    skill_score,
                    semantic_score,
                    experience,
                    project_score
                )

                # STATUS
                status = calculate_selection(
                    final_score,
                    experience
                )

                # NAME
                candidate_name = os.path.splitext(
                    secure_filename(
                        file.filename
                    )
                )[0]

                # DATABASE
                try:

                    save_candidate(
                        candidate_name,
                        role,
                        final_score,
                        experience,
                        status
                    )

                except Exception as db_error:

                    print(
                        "Database error:",
                        db_error
                    )

                # RESULT
                results.append({

                    "name": candidate_name,

                    "role": role,

                    "score": round(
                        final_score,
                        2
                    ),

                    "skill_score": round(
                        skill_score,
                        2
                    ),

                    "semantic_score": round(
                        semantic_score,
                        2
                    ),

                    "project_score": round(
                        project_score,
                        2
                    ),

                    "ranking_score": round(
                        ranking_score,
                        2
                    ),

                    "ranking_status": ranking_status,

                    "experience": experience,

                    "status": status,

                    "matched_skills": matched_skills,

                    "missing_skills": missing_skills

                })

            except Exception as e:

                print(
                    "Resume processing error:",
                    e
                )

                results.append({

                    "name": file.filename,

                    "role": "Error",

                    "score": 0,

                    "skill_score": 0,

                    "semantic_score": 0,

                    "project_score": 0,

                    "ranking_score": 0,

                    "ranking_status": "Error",

                    "experience": 0,

                    "status": "Error",

                    "matched_skills": [],

                    "missing_skills": [],

                    "error": str(e)

                })

    # ========================================================
    # RENDER RESULTS
    # ========================================================

    return render_template(
        "bulk_upload.html",
        results=results
    )


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )