# SkillGap AI

**AI-Powered Skill Gap Analyzer and Personalized Learning Assistant**

## 🚀 Project Overview

SkillGap AI is a complete full-stack web application designed to help students bridge the gap between their current skills and their career goals. It analyzes a student's resume, conducts a personalized skill assessment, identifies missing and weak skills based on industry requirements, and generates a customized learning roadmap with curated course recommendations.

## ✨ Features

- **Resume Skill Extraction:** Upload a PDF or DOCX resume to automatically extract technical skills.
- **Career Goal Analysis:** Select a target job role and see exactly what skills you need.
- **Dynamic Skill Assessment:** Take a tailored multiple-choice test based on your current skills.
- **Skill Gap Detection:** Discover your Strong, Weak, and Missing skills.
- **Course Recommendations:** Get clickable links to free, high-quality learning resources (YouTube, Coursera, Kaggle, etc.).
- **Personalized Roadmap:** Follow a step-by-step learning journey and track your progress.
- **Analysis History:** Save and review your past analyses as you improve.
- **Beautiful Dashboard:** Clean, modern, and responsive UI built for students.

## 🛠️ Technology Stack

**Frontend:**
- React (Vite)
- Standard CSS (Custom Design System)
- React Router DOM (Navigation)
- Chart.js (Visualizations)
- Lucide React (Icons)
- Axios (API Client)

**Backend & AI Logic:**
- Python 3
- Flask (REST API)
- SQLite (Lightweight database)
- pdfplumber & python-docx (Resume parsing)
- Regex & NLP logic (Skill matching & gap calculation)
- bcrypt & JWT (Authentication)

---

## 💻 How to Run the Project Locally

Follow these simple steps to get the project running on your local machine.

### 1. Backend Setup (Flask API)

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd SkillGap-AI/backend
   ```
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   python app.py
   ```
   *The database will be automatically created on the first run. The server will start at `http://localhost:5000`.*

### 2. Frontend Setup (React/Vite)

1. Open a **new** terminal window and navigate to the `frontend` folder:
   ```bash
   cd SkillGap-AI/frontend
   ```
2. Install the Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and go to: **`http://localhost:5173`**

---

## 🧠 How It Works Internally

### Resume Analysis
When a resume is uploaded, the backend uses `pdfplumber` (for PDF) or `python-docx` (for DOCX) to extract raw text. It then uses regex-based boundary matching against a predefined skills database (`data/skills.csv`) to accurately identify known programming languages, tools, and concepts while handling aliases (e.g., "JS" -> "JavaScript").

### Skill Gap Analysis
The system retrieves the required skills for the user's selected career goal (`data/job_roles.csv`). It compares the extracted resume skills with the required skills. Missing skills are those required but not in the resume. Matched skills are further categorized into "Strong" or "Weak" based on the user's performance in the dynamically generated assessment test.

### Recommendations
The recommender service matches the identified Weak and Missing skills with a curated dataset of learning resources (`data/courses.csv`), ensuring the user gets direct links to platforms like YouTube, Coursera, and freeCodeCamp.

---

## 🔮 Future Scope

- Integration with LinkedIn/GitHub APIs for automated profile fetching.
- Integration with an LLM (like Gemini or OpenAI) for conversational interview prep.
- Real-time job market scraping to dynamically update job skill requirements.
- Social features: sharing roadmaps with peers or college professors.

*Built as a college project demonstrating practical AI, full-stack development, and clean UI/UX design.*
