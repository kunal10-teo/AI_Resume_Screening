
from flask import Flask, request, render_template, session, redirect, url_for
import joblib
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
# DATABASE
# ============================================================

from database import save_candidate, get_candidates

# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = "resume_screening_secret"

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
    """
    Normalize text for better skill matching.
    """

    text = text.lower()

    # Replace common separators with spaces
    text = re.sub(r"[/|,;:()\[\]{}]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):
    """
    Extract known technical skills from text.
    """

    text = normalize_text(text)

    found_skills = []

    for skill in skills_list:

        skill_normalized = normalize_text(skill)

        # Word-boundary matching
        pattern = r"(?<!\w)" + re.escape(skill_normalized) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):
    """
    Extract maximum years of experience from resume text.
    """

    text = text.lower()

    experience_values = []

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)\s+(?:of\s+)?experience",
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text)

        for value in matches:

            try:
                experience_values.append(float(value))
            except ValueError:
                pass

    if experience_values:
        return max(experience_values)

    return 0


# ============================================================
# TF-IDF SIMILARITY
# ============================================================

def calculate_similarity(resume, job):
    """
    Calculate semantic similarity using TF-IDF.
    """

    resume = normalize_text(resume)
    job = normalize_text(job)

    if not resume or not job:
        return 0.0

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        vectors = vectorizer.fit_transform(
            [resume, job]
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(similarity * 100, 2)

    except Exception as e:

        print("Similarity error:", e)

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
    """
    Calculate a weighted ATS score.

    60% = Skill matching
    40% = TF-IDF job-description similarity
    """

    # --------------------------------------------------------
    # Skill Match
    # --------------------------------------------------------

    if job_skills:

        matched_skills = [
            skill
            for skill in job_skills
            if skill in resume_skills
        ]

        skill_score = (
            len(matched_skills) /
            len(job_skills)
        ) * 100

    else:

        matched_skills = []
        skill_score = 0

    # --------------------------------------------------------
    # Text Similarity
    # --------------------------------------------------------

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    # --------------------------------------------------------
    # Final ATS Score
    # --------------------------------------------------------

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

    return round(final_score, 2), matched_skills


# ============================================================
# CANDIDATE STATUS
# ============================================================

def calculate_selection(score, experience):

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

@app.route("/", methods=["GET", "POST"])
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

        file = request.files.get("resume")

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
        # Extract Resume Skills
        # ----------------------------------------------------

        skills_found = extract_skills(
            resume_text
        )

        # ----------------------------------------------------
        # Extract Job Skills
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

        print("\n==============================")
        print("AI RESUME SCREENING RESULT")
        print("==============================")
        print("Name:", name)
        print("Predicted Role:", result)
        print("ATS Score:", score)
        print("Similarity:", similarity_score)
        print("Skill Score:", skill_score)
        print("Experience:", experience)
        print("Matched Skills:", matched_skills)
        print("Missing Skills:", missing_skills)
        print("Status:", selection)
        print("==============================\n")

    # --------------------------------------------------------
    # Render Home Page
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
        )

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
                url_for("dashboard")
            )

        return "Invalid Login"

    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:

        return redirect(
            url_for("login")
        )

    candidates = get_candidates()

    return render_template(
        "dashboard.html",
        candidates=candidates
    )


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

