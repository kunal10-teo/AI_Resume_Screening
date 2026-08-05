from flask import Flask, request, render_template, session, redirect, url_for
import joblib
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import sys
import os


# Root folder access
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from database import save_candidate, get_candidates


app = Flask(
    __name__,
    template_folder="../templates"
)


app.secret_key = "resume_screening_secret"


# Load Model
model = joblib.load(
    "models/resume_model.pkl"
)



skills_list = [
    "python",
    "sql",
    "machine learning",
    "pandas",
    "numpy",
    "java",
    "javascript",
    "html",
    "css",
    "react",
    "aws",
    "docker",
    "git"
]


required_skills = [
    "python",
    "sql",
    "machine learning",
    "pandas",
    "numpy",
    "git",
    "docker",
    "aws"
]



def calculate_match(resume, job):

    documents = [
        resume,
        job
    ]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(
        documents
    )

    score = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )

    return round(
        score[0][0] * 100,
        2
    )



def extract_experience(text):

    pattern = r'(\d+)\+?\s*(?:years|year|yrs)'

    experience = re.findall(
        pattern,
        text
    )


    if experience:

        return max(
            map(int, experience)
        )


    return 0



# Home Page
@app.route("/", methods=["GET","POST"])
def home():

    result = ""
    skills_found = []
    missing_skills = []

    score = 0
    experience = 0
    selection = ""


    if request.method == "POST":


        name = request.form.get(
            "name",
            "Unknown"
        )


        file = request.files["resume"]


        job_description = request.form.get(
            "job_description",
            ""
        )



        reader = PdfReader(file)


        resume_text = ""


        for page in reader.pages:

            text = page.extract_text()

            if text:

                resume_text += text.lower()



        prediction = model.predict(
            [resume_text]
        )


        result = prediction[0]



        experience = extract_experience(
            resume_text
        )



        for skill in skills_list:

            if skill in resume_text:

                skills_found.append(skill)



        for skill in required_skills:

            if skill not in skills_found:

                missing_skills.append(skill)



        if job_description:

            score = calculate_match(
                resume_text,
                job_description.lower()
            )



        if score >= 70 and experience >= 1:

            selection = "Selected ✅"

        else:

            selection = "Rejected ❌"



        save_candidate(
            name,
            result,
            score,
            experience,
            selection
        )



    return render_template(
        "index.html",
        result=result,
        skills=skills_found,
        missing=missing_skills,
        score=score,
        experience=experience,
        selection=selection
    )




# Login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")


        if username == "admin" and password == "12345":

            session["admin"] = True

            return redirect(
                url_for("dashboard")
            )


        return "Invalid Login"


    return render_template(
        "login.html"
    )




# Dashboard
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




# Logout
@app.route("/logout")
def logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for("login")
    )




if __name__ == "__main__":

    app.run(debug=True)