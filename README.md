# SkillGap AI

**AI-Powered Skill Gap Analyzer and Personalized Learning Assistant**

## 🚀 Project Overview

SkillGap AI is a full-stack web application designed to help college students bridge the gap between their current academic skills and their career goals. It analyzes a student's resume, conducts a personalized skill assessment, identifies missing and weak skills based on industry requirements, and generates a customized learning roadmap with curated course recommendations. The platform also includes a practice quiz module with explanations and an AI career assistant to support students throughout their preparation.

---

## ✨ Features

- **Resume Skill Extraction (PDF and DOCX):** Upload a resume in PDF or DOCX format to automatically extract technical skills using pattern matching and aliases. Extracted skills can also be manually reviewed and edited.
- **Career Goal / Job Role Selection:** Choose from predefined industry job roles (such as Data Scientist, Web Developer, Machine Learning Engineer) to view the required technical skill set.
- **Skill Assessment:** Take a dynamically generated multiple-choice assessment test based on extracted resume skills and the selected career goal.
- **Skill Gap Analysis:** Automatically categorize skills into **Strong** (verified by assessment), **Weak** (found in resume but needs practice), and **Missing** (required by the role but absent from resume), alongside a calculated Career Readiness Score.
- **Course Recommendations:** Receive curated recommendations linking directly to high-quality, free educational resources from platforms like YouTube, Coursera, freeCodeCamp, and Kaggle.
- **Personalized Learning Roadmap:** Follow a structured step-by-step learning plan broken into manageable phases, with interactive checkboxes to track completion progress.
- **Practice Quiz:** Practice individual technical topics (Python, SQL, Machine Learning, HTML and CSS, JavaScript, Data Analysis) across Beginner, Intermediate, and Advanced difficulties with immediate explanations and why-wrong option feedback.
- **Career Assistant:** Ask questions through a student-friendly chat interface that gives tailored advice on career roadmaps, skill improvement, project ideas, and interview preparation using the student's profile context.
- **Student Profile:** Manage personal and educational details, including degree, college, branch/specialization, target career domain, weekly available study hours, self-reported skills, and portfolio links.
- **Light and Dark Mode:** Seamlessly toggle between dark and light themes with user preference saved in the browser.
- **Student Dashboard:** View a quick summary of current readiness, extracted skills, target goal, recent assessment scores, and fast navigation shortcuts.
- **Analysis History:** Review past skill gap reports and track test/quiz attempt scores over time to measure improvement.

---

## 🛠️ Technology Stack

### Frontend
- **React (v19):** UI library for building the single-page application.
- **Vite:** Next-generation frontend build tool and local development server.
- **React Router DOM (v7):** Handles client-side routing, navigation, and protected routes.
- **Axios:** Handles HTTP requests and communication with the Flask REST API.
- **Chart.js & react-chartjs-2:** Renders visual analytics charts for scores and historical performance.
- **Lucide React:** Icon library for consistent and clean interface icons.
- **React Hot Toast:** Lightweight notifications for user actions and feedback.
- **Vanilla CSS:** Custom design system using CSS variables for theme support and responsive layouts.

### Backend
- **Python 3:** Core programming language.
- **Flask:** Lightweight REST API framework.
- **Flask-CORS:** Enables Cross-Origin Resource Sharing between the React frontend and Flask backend.
- **Flask-JWT-Extended:** Manages stateless JSON Web Token (JWT) user authentication.
- **SQLite3:** Embedded relational database used to store users, profiles, resumes, quiz attempts, and analysis results without requiring separate database installation.
- **pdfplumber & python-docx:** Libraries used to read and extract plain text from uploaded PDF and DOCX resume files.
- **bcrypt:** Provides password hashing for secure authentication.
- **Werkzeug:** Utility library for secure file upload handling and HTTP helpers.
- **Regex & Built-in Modules:** Uses Python's built-in `re`, `csv`, and `sqlite3` modules for alias-based skill extraction and data processing. *(Note: `pandas` and `scikit-learn` are included in `requirements.txt` for optional data science tasks, while core application routes use lightweight built-in Python utilities).*

---

## 📊 Data Files

The `data/` folder contains essential reference datasets stored in CSV format:

- **`data/skills.csv`:** Contains over 45 technical skills alongside their common aliases and abbreviations (e.g., "JS" for JavaScript, "Sklearn" for Scikit-learn). The resume extractor uses these aliases with word-boundary regular expressions to detect skills accurately in resume text.
- **`data/job_roles.csv`:** Maps 11 tech job roles (e.g., Data Scientist, Machine Learning Engineer, Web Developer, Cloud Engineer) to their industry-expected required skills. This acts as the benchmark for identifying missing skills.
- **`data/courses.csv`:** A curated catalog of free learning resources and tutorials mapped to specific technical skills, complete with course titles, platforms (YouTube, Coursera, Kaggle), duration, and clickable URLs.
- **`data/questions.csv`:** A question bank containing over 180 multiple-choice questions across different skills and difficulty levels. Each question contains options, correct answers, detailed conceptual explanations, and reasons why incorrect options are wrong.

---

## 💻 How to Run the Project Locally (Windows)

Follow these step-by-step instructions to run both the backend and frontend on Windows.

### Prerequisites
- Python 3.10 or higher installed with **"Add Python to PATH"** enabled.
- Node.js (v18 or higher recommended) and npm installed.

---

### 1. Backend Setup (Flask API)

1. Open PowerShell or Command Prompt and navigate to the `backend` folder:
   ```bash
   cd SkillGap-AI/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
   *(If you see an execution policy error in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

4. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the Flask backend server:
   ```bash
   python app.py
   ```
   *The SQLite database file (`skillgap.db`) will be automatically initialized on first run. The API runs at:*
   ```text
   http://localhost:5000
   ```

---

### 2. Frontend Setup (React / Vite)

1. Open a **new, separate terminal window** and navigate to the `frontend` folder:
   ```bash
   cd SkillGap-AI/frontend
   ```

2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your web browser and navigate to the local address displayed in your terminal:
   ```text
   http://localhost:5173
   ```
   *(Note: If port `5173` is already in use by another terminal, Vite will automatically use the next available port, such as `http://localhost:5174`).*

---

## 🧠 How It Works Internally

### Resume Analysis
When a student uploads a resume (`.pdf` or `.docx`), the backend extracts raw text using `pdfplumber` or `python-docx`. The text is sanitized and matched against `data/skills.csv` using boundary-aware regex patterns. Recognized skill names and aliases are mapped to canonical skill titles and saved to the database.

### Skill Gap Analysis
When a student selects a career goal, the backend loads the benchmark skill requirements from `data/job_roles.csv`. It compares the student's extracted skills against the role requirements:
- **Missing Skills:** Skills required by the role that are not present in the student's resume.
- **Matched Skills:** Skills found in both the resume and the job role requirements.

### Assessment & Dynamic Categorization
Matched skills are tested through dynamically selected multiple-choice questions from `data/questions.csv`. Based on the score:
- Skills with high accuracy are classified as **Strong Skills**.
- Skills with low accuracy or incorrect responses are classified as **Weak Skills**.
- The overall **Career Readiness Score (%)** is calculated based on verified skills relative to the total requirements for that role.

### Course & Roadmap Recommendations
The application matches identified Weak and Missing skills against `data/courses.csv` to present direct links to free learning content. A week-by-week learning roadmap is generated, allowing students to track their progress from fundamental concepts to practical projects.

---

## 🔮 Future Scope

- Integration with LinkedIn and GitHub APIs for automatic profile and repository analysis.
- Integration with an LLM API (such as Google Gemini or OpenAI) for open-ended conversational mock interviews.
- Real-time job market web scraping to dynamically update industry skill demands.
- Exporting skill gap reports and learning roadmaps as downloadable PDF summaries.
- Social features for sharing learning roadmaps with peers or college mentors.

---

*SkillGap AI – Built as a college semester project demonstrating practical AI, full-stack development, and clean UI/UX design.*
