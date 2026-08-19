# 🤖 AI Resume Screening System

An AI-powered Resume Screening System that automatically analyzes resumes, predicts suitable job roles, calculates ATS match scores, extracts skills, detects missing skills, identifies experience, and helps recruiters shortlist candidates.

## 🚀 Features

* 📄 Resume PDF Upload
* 🤖 AI-Based Job Role Prediction
* 🧠 NLP-Based Resume Analysis
* 📊 ATS Match Percentage Calculation
* 🛠️ Skill Extraction
* ❌ Missing Skill Detection
* 💼 Experience Detection
* ✅ Candidate Selection — Selected / Rejected
* 🗄️ SQLite Database Integration
* 🔐 Admin Login System
* 📋 Recruiter Dashboard
* 📑 Bulk Resume Screening

## 🛠️ Technologies Used

### Programming Language

* Python

### Machine Learning & NLP

* Scikit-learn
* TF-IDF Vectorizer
* Machine Learning Classification Model

### Backend

* Flask
* Gunicorn

### Database

* SQLite

### Data Processing

* Pandas
* NumPy

### PDF & Model Processing

* PyPDF
* Joblib

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

## 📂 Project Structure

```text
AI_Resume_Screening/
│
├── app/
├── data/
├── models/
├── src/
├── templates/
│
├── main.py
├── database.py
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kunal10-teo/AI_Resume_Screening.git
cd AI_Resume_Screening
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 📊 How It Works

```text
Resume PDF
     ↓
PDF Text Extraction
     ↓
NLP Processing
     ↓
Skill Extraction
     ↓
Job Role Prediction
     ↓
ATS Match Score
     ↓
Experience Detection
     ↓
Candidate Ranking
     ↓
Selected / Rejected
     ↓
Recruiter Dashboard
```

## 📸 Screenshots

### 🏠 Home Page

Add your Home Page screenshot here.

### 📊 Resume Analysis Result

Add your Resume Analysis screenshot here.

### 🔐 Admin Login

Add your Admin Login screenshot here.

### 📋 Admin Dashboard

Add your Admin Dashboard screenshot here.

## 🗄️ Database

The project uses SQLite to store candidate information and screening history.

The system can store:

* Candidate name
* Predicted job role
* ATS score
* Experience
* Selection status

## 🚀 Deployment

The application is configured for deployment using:

* Gunicorn
* Render
* `render.yaml`

## 🎯 Use Cases

This project can be used by:

* Recruiters
* HR Teams
* Startups
* Placement Cells
* Companies handling large numbers of resumes

## 🔮 Future Improvements

* Advanced NLP using Transformer models
* Resume ranking using semantic similarity
* Multiple job description support
* Email notification system
* Cloud database integration
* Candidate analytics
* Authentication and role-based access
* Advanced recruiter analytics dashboard

## 👨‍💻 Author

**Kunal Teotia**

GitHub:
https://github.com/kunal10-teo

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.
