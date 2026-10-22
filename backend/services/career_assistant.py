"""
SkillGap AI - Career Assistant Service
======================================
Rule-based Career Advisor designed specifically for college students.
Provides practical, beginner-friendly advice on technical skills,
project building, learning roadmaps, and interview preparation.
Utilizes existing profile, resume, and skill gap data as context.
No paid APIs or external dependencies required.
"""

import os
import csv
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")


def _load_job_roles():
    """Load job roles and required skills from data/job_roles.csv."""
    roles = {}
    csv_path = os.path.join(DATA_DIR, "job_roles.csv")
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                role = row.get("job_role", "").strip()
                skills = [s.strip() for s in row.get("required_skills", "").split(",") if s.strip()]
                roles[role] = skills
    return roles


def _load_courses():
    """Load courses from data/courses.csv grouped by skill."""
    courses_by_skill = {}
    csv_path = os.path.join(DATA_DIR, "courses.csv")
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = row.get("skill", "").strip().lower()
                if skill not in courses_by_skill:
                    courses_by_skill[skill] = []
                courses_by_skill[skill].append(row)
    return courses_by_skill


JOB_ROLES = _load_job_roles()
COURSES_BY_SKILL = _load_courses()


# ── Curated Roadmaps by Role ────────────────────────────────────────────────
ROADMAPS = {
    "data analyst": (
        "### 🗺️ Beginner-Friendly Data Analyst Roadmap\n\n"
        "**Phase 1: Foundations & Spreadsheets (Weeks 1–3)**\n"
        "- Master **Microsoft Excel**: Pivot Tables, VLOOKUP/XLOOKUP, conditional formatting, and basic data cleaning.\n"
        "- Learn basic statistics: Mean, median, standard deviation, probability distributions, and correlation.\n\n"
        "**Phase 2: Relational Databases & SQL (Weeks 4–6)**\n"
        "- SQL fundamentals: `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, and sorting.\n"
        "- Intermediate SQL: `INNER/LEFT/RIGHT JOIN`, subqueries, and window functions (`ROW_NUMBER`, `RANK`).\n"
        "- Practice on LeetCode (Database) or HackerRank SQL.\n\n"
        "**Phase 3: Python for Data Analysis (Weeks 7–10)**\n"
        "- Python basics (loops, functions, lists, dictionaries).\n"
        "- **Pandas & NumPy**: Dataframes, slicing, handling missing values, filtering, grouping.\n"
        "- **Matplotlib & Seaborn**: Bar charts, line plots, heatmaps, histograms.\n\n"
        "**Phase 4: BI & Data Visualization Tools (Weeks 11–13)**\n"
        "- Master either **Power BI** or **Tableau**.\n"
        "- Build interactive executive dashboards with KPIs, slicers, and drill-downs.\n\n"
        "**Phase 5: Portfolio & Case Studies (Weeks 14+)**\n"
        "- Build 2–3 portfolio projects using real Kaggle or government datasets.\n"
        "- Publish reports and SQL queries on GitHub and write project summaries on LinkedIn."
    ),
    "machine learning engineer": (
        "### 🗺️ Beginner-Friendly Machine Learning Engineer Roadmap\n\n"
        "**Phase 1: Math & Programming Core (Weeks 1–4)**\n"
        "- **Python**: Advanced data structures, OOP, file handling, NumPy vectorization.\n"
        "- **Essential Math**: Linear algebra (matrices, eigenvalues), Calculus (derivatives, gradients), Statistics & Probability.\n\n"
        "**Phase 2: Data Handling & Exploratory Analysis (Weeks 5–7)**\n"
        "- **Pandas & NumPy**: Data cleaning, feature transformation, handling outliers.\n"
        "- Data Visualization: Matplotlib, Seaborn, exploratory data analysis (EDA).\n"
        "- Version control: Git and GitHub for tracking experiments.\n\n"
        "**Phase 3: Classical Machine Learning (Weeks 8–12)**\n"
        "- **Scikit-learn**: Linear/Logistic Regression, Decision Trees, Random Forests, Gradient Boosting (XGBoost/LightGBM), SVM, K-Means.\n"
        "- Model Evaluation: Cross-validation, Precision/Recall, F1-score, ROC-AUC, bias-variance tradeoff.\n\n"
        "**Phase 4: Deep Learning Foundations (Weeks 13–17)**\n"
        "- Neural Networks basics: Perceptrons, Backpropagation, Activation functions.\n"
        "- Framework: **PyTorch** or **TensorFlow**.\n"
        "- CNNs for computer vision or Transformers/RNNs for NLP.\n\n"
        "**Phase 5: MLOps & Deployment (Weeks 18+)**\n"
        "- Package models into REST APIs using **Flask** or **FastAPI**.\n"
        "- Containerize with **Docker** and track metrics.\n"
        "- Deploy on Hugging Face Spaces, Render, or AWS EC2."
    ),
    "data scientist": (
        "### 🗺️ Beginner-Friendly Data Scientist Roadmap\n\n"
        "**Phase 1: Python, Math & EDA (Month 1)**\n"
        "- Python core, Pandas, NumPy, Jupyter Notebooks.\n"
        "- Descriptive and inferential statistics, hypothesis testing (p-values, A/B testing).\n\n"
        "**Phase 2: SQL & Advanced Data Wrangling (Month 2)**\n"
        "- Complex SQL queries, CTEs, aggregation, data pipeline hygiene.\n"
        "- Data cleaning, feature engineering, and exploratory data visualization.\n\n"
        "**Phase 3: Supervised & Unsupervised Machine Learning (Month 3)**\n"
        "- Scikit-learn algorithms: Regression, Classification, Clustering, PCA.\n"
        "- Hyperparameter tuning with GridSearchCV / Optuna.\n\n"
        "**Phase 4: Deep Learning & Modern AI (Month 4)**\n"
        "- PyTorch or TensorFlow fundamentals.\n"
        "- Introduction to LLM prompting, embeddings, and NLP basics.\n\n"
        "**Phase 5: Business Storytelling & Deployment (Month 5+)**\n"
        "- Translating model metrics into business insights.\n"
        "- Building web demos using Streamlit or Flask.\n"
        "- Documenting findings in clean GitHub repositories and portfolio decks."
    ),
    "web developer": (
        "### 🗺️ Beginner-Friendly Web Developer Roadmap\n\n"
        "**Phase 1: Web Fundamentals (Weeks 1–3)**\n"
        "- **HTML5**: Semantic tags, forms, tables, accessibility.\n"
        "- **CSS3**: Box model, Flexbox, CSS Grid, media queries for responsive design.\n\n"
        "**Phase 2: JavaScript Core (Weeks 4–7)**\n"
        "- Variables (`let`/`const`), functions, arrow functions, template literals.\n"
        "- DOM manipulation, event listeners, array methods (`map`, `filter`, `reduce`).\n"
        "- Asynchronous JS: Promises, `async/await`, Fetch API / Axios.\n\n"
        "**Phase 3: Modern Frontend with React (Weeks 8–11)**\n"
        "- Components, JSX, Props, and State (`useState`, `useEffect`).\n"
        "- Routing with React Router DOM.\n"
        "- State management (Context API) and styling patterns.\n\n"
        "**Phase 4: Tooling & Full-Stack Basics (Weeks 12+)**\n"
        "- Vite / npm, Git & GitHub workflow.\n"
        "- Connecting to REST APIs, handling error states and loading spinners.\n"
        "- Deploying on Vercel, Netlify, or GitHub Pages."
    ),
    "full stack developer": (
        "### 🗺️ Beginner-Friendly Full Stack Developer Roadmap\n\n"
        "**Phase 1: Frontend Mastery (Weeks 1–6)**\n"
        "- HTML5, CSS3 (Flexbox/Grid), JavaScript ES6+.\n"
        "- React: Hooks, Context API, React Router, Axios for API calls.\n\n"
        "**Phase 2: Backend Development (Weeks 7–11)**\n"
        "- Backend runtime: Node.js (with Express) OR Python (with Flask/FastAPI).\n"
        "- RESTful API design: Endpoints, status codes, query/body params, middleware.\n"
        "- Authentication: JWT tokens, password hashing with bcrypt.\n\n"
        "**Phase 3: Database & ORM (Weeks 12–15)**\n"
        "- Relational DB: PostgreSQL / MySQL / SQLite.\n"
        "- NoSQL DB: MongoDB with Mongoose.\n"
        "- Schema design, relationships (1-to-many, many-to-many), indexing.\n\n"
        "**Phase 4: Full Stack Integration & Deployment (Weeks 16+)**\n"
        "- Connect React frontend to Flask/Node backend with proper CORS.\n"
        "- Environment variables (`.env`) for secrets.\n"
        "- Deployment: Render, Vercel, Supabase, or Railway."
    ),
    "software developer": (
        "### 🗺️ Beginner-Friendly Software Developer Roadmap\n\n"
        "**Phase 1: Core Programming Language & OOP (Weeks 1–4)**\n"
        "- Pick one language: Python, Java, or C++.\n"
        "- Object-Oriented Programming (OOP): Classes, inheritance, polymorphism, encapsulation.\n\n"
        "**Phase 2: Data Structures & Algorithms (Weeks 5–10)**\n"
        "- Arrays, Strings, Linked Lists, Stacks, Queues, Hash Tables.\n"
        "- Trees (Binary Trees, BST), Graphs, Recursion, Dynamic Programming.\n"
        "- Practice 1–2 LeetCode problems daily (Easy -> Medium).\n\n"
        "**Phase 3: Software Engineering Practices (Weeks 11–13)**\n"
        "- Version control with Git (branches, pull requests, merge conflict resolution).\n"
        "- Unit testing, debugging techniques, clean code principles (SOLID, DRY).\n\n"
        "**Phase 4: Databases & System Fundamentals (Weeks 14+)**\n"
        "- SQL database fundamentals and query optimization.\n"
        "- OS concepts (processes, threads, memory) and computer networking basics (HTTP, TCP/IP).\n"
        "- Build a full-featured capstone application with persistent storage."
    ),
    "cloud engineer": (
        "### 🗺️ Beginner-Friendly Cloud Engineer Roadmap\n\n"
        "**Phase 1: Operating Systems & Networking (Weeks 1–4)**\n"
        "- Linux command line, bash scripting, file permissions, SSH.\n"
        "- Networking: IP addressing, subnets, DNS, HTTP/HTTPS, firewalls, VPC concepts.\n\n"
        "**Phase 2: Cloud Provider Foundations (Weeks 5–8)**\n"
        "- Choose **AWS** (or Azure / GCP).\n"
        "- Core services: Compute (EC2), Storage (S3), Database (RDS), Identity & Access (IAM).\n"
        "- Aim for entry certification: AWS Certified Cloud Practitioner.\n\n"
        "**Phase 3: Containers & Orchestration (Weeks 9–12)**\n"
        "- Docker: Dockerfiles, building images, container networking, Docker Compose.\n"
        "- Kubernetes basics: Pods, Services, Deployments.\n\n"
        "**Phase 4: Infrastructure as Code & CI/CD (Weeks 13+)**\n"
        "- Terraform basics for provisioning infrastructure.\n"
        "- CI/CD pipelines with GitHub Actions or Jenkins.\n"
        "- Monitoring with CloudWatch / Prometheus."
    ),
    "devops engineer": (
        "### 🗺️ Beginner-Friendly DevOps Engineer Roadmap\n\n"
        "**Phase 1: Linux & Scripting (Weeks 1–4)**\n"
        "- Linux system administration, process management, log inspection.\n"
        "- Shell/Bash scripting and Python for automation.\n\n"
        "**Phase 2: Version Control & CI/CD (Weeks 5–8)**\n"
        "- Advanced Git: Rebase, cherry-pick, merge strategies.\n"
        "- Automated pipelines with GitHub Actions, GitLab CI, or Jenkins.\n\n"
        "**Phase 3: Containers & Infrastructure as Code (Weeks 9–13)**\n"
        "- Docker containerization for multiple tech stacks.\n"
        "- Kubernetes cluster management.\n"
        "- Terraform for declarative cloud infrastructure.\n\n"
        "**Phase 4: Monitoring & Cloud Operations (Weeks 14+)**\n"
        "- Centralized logging (ELK stack) and metrics (Prometheus & Grafana).\n"
        "- Cloud security best practices and automated rollbacks."
    ),
    "cybersecurity analyst": (
        "### 🗺️ Beginner-Friendly Cybersecurity Analyst Roadmap\n\n"
        "**Phase 1: IT & Networking Foundations (Weeks 1–4)**\n"
        "- OSI model, TCP/IP, DNS, DHCP, routing, and switching.\n"
        "- Linux administration and Windows security fundamentals.\n\n"
        "**Phase 2: Security Concepts & Cryptography (Weeks 5–8)**\n"
        "- CIA Triad, symmetric vs asymmetric encryption, hashing, SSL/TLS.\n"
        "- Common attack vectors: Phishing, SQL Injection, XSS, Man-in-the-Middle, Ransomware.\n\n"
        "**Phase 3: Defensive Tools & SIEM (Weeks 9–12)**\n"
        "- Network packet analysis using **Wireshark**.\n"
        "- Vulnerability scanning using **Nmap**.\n"
        "- SIEM log analysis tools (Splunk, ELK, or Wazuh).\n\n"
        "**Phase 4: Labs & Certifications (Weeks 13+)**\n"
        "- Hands-on practice on platforms: TryHackMe and Hack The Box.\n"
        "- Target entry certifications: CompTIA Security+ or Google Cybersecurity Certificate."
    ),
}


# ── Project Ideas by Domain ─────────────────────────────────────────────────
PROJECT_IDEAS = {
    "data analyst": [
        "**E-Commerce Sales & Profit Dashboard (Excel / Power BI / SQL)**: Clean 50,000+ transaction rows in SQL, calculate KPIs (Customer Lifetime Value, churn rate, monthly revenue), and present interactive visuals with date slicers.",
        "**Real-Estate Price Analysis (Python & Pandas)**: Scrape or use Kaggle real-estate data to analyze the impact of square footage, location, and bedroom count on property pricing with Seaborn visualizations.",
        "**COVID-19 or Global Health Metrics Tracker (SQL & Tableau)**: Write complex multi-table joins and window functions in SQL to aggregate hospitalization and recovery rates, then build a drill-down dashboard.",
    ],
    "machine learning engineer": [
        "**End-to-End Customer Churn Predictor (Scikit-Learn + Flask + Docker)**: Train Random Forest & XGBoost models with hyperparameter tuning, build a Flask REST API endpoint, containerize with Docker, and evaluate with Precision-Recall curves.",
        "**Image Classification or Defect Detector (PyTorch / CNN)**: Train a Convolutional Neural Network on CIFAR-10 or Kaggle medical/manufacturing scans with data augmentation and confusion matrix evaluation.",
        "**AI Resume & Job Matcher (NLP / TF-IDF / Embeddings)**: Extract text from PDF resumes, calculate cosine similarity against job descriptions, and highlight missing keywords.",
    ],
    "web developer": [
        "**Responsive Developer Portfolio & Blog (React + CSS)**: Interactive portfolio with dark/light mode toggle, markdown blog viewer, filterable project gallery, and working contact form.",
        "**Task & Productivity Kanban Board (React + LocalStorage / Firebase)**: Drag-and-drop tasks between To-Do, In Progress, and Completed states, with search, tags, and persistence.",
        "**Weather & Air Quality Dashboard (React + OpenWeather API)**: Geolocation-based weather forecasting with 5-day trends, interactive charts, and loading/error states.",
    ],
    "full stack developer": [
        "**Student Learning Portal / Skill Gap Analyzer (React + Flask / Node + SQLite / PostgreSQL)**: Full authentication with JWT, protected routes, resume parsing or file uploads, and personalized roadmaps.",
        "**Collaborative Note-Taking & Documentation App**: Markdown editor with auto-save, tag-based search, user auth, and PDF export functionality.",
        "**E-Commerce Mini-Store with Cart & Checkout**: Product catalog with filtering, persistent shopping cart, mock Stripe checkout, and order history.",
    ],
    "software developer": [
        "**CLI File Management & Backup Tool (Python / C++)**: Command-line utility to monitor directories, automatically compress and encrypt backups, and log operations.",
        "**Multi-Threaded Web Crawler / Scraper**: Python or Java crawler using worker threads/asyncio to fetch, parse, and store page metadata with rate-limiting.",
        "**In-Memory Key-Value Store with TTL**: Build a lightweight Redis clone supporting GET, SET, EXPIRE, and persistent snapshots to disk.",
    ],
}


# ── Interview Preparation Guides ─────────────────────────────────────────────
INTERVIEW_GUIDE = (
    "### 🎯 Comprehensive Technical Interview Preparation Guide\n\n"
    "**1. Data Structures & Algorithms (Coding Rounds)**\n"
    "- **Core topics to master**: Arrays, Hash Maps, Two Pointers, Sliding Window, Linked Lists, Binary Search, Trees (BFS/DFS), and basic Dynamic Programming.\n"
    "- **Practice Strategy**: Solve 75 essential problems (like the Blind 75 or NeetCode 150) rather than hundreds of random ones.\n"
    "- **During the interview**: Always clarify requirements, state edge cases (empty input, null, negative numbers), talk through your thought process *before* coding, and analyze Time & Space Complexity (Big-O).\n\n"
    "**2. Technical Domain & Resume Deep-Dive**\n"
    "- Be ready to explain every single project on your resume inside and out.\n"
    "- Know **why** you chose a specific technology (e.g., *'Why did you choose Flask over Django?'* or *'Why did you choose React over plain JS?'*).\n"
    "- Highlight real engineering trade-offs and bugs you diagnosed and fixed.\n\n"
    "**3. Behavioral Round (STAR Method)**\n"
    "- Structure answers using **S**ituation, **T**ask, **A**ction, **R**esult.\n"
    "- Prepare 4 concrete stories: A difficult technical bug, a time you had a deadline crunch, a disagreement in a team project, and a project you are proud of.\n\n"
    "**4. Questions to Ask the Interviewer**\n"
    "- *'What does the typical day-to-day workflow look like for an intern/junior engineer on this team?'*\n"
    "- *'Which technologies or architectural challenges is the engineering team currently tackling?'*"
)


def _format_skill_advice(skill_name: str) -> str:
    """Generate comprehensive skill improvement advice for a specific skill."""
    skill_lower = skill_name.lower().strip()
    
    # Check if courses exist in database
    courses = COURSES_BY_SKILL.get(skill_lower, [])
    
    response = f"### 💡 How to Master and Improve Your **{skill_name.capitalize()}** Skills\n\n"
    
    if skill_lower == "python":
        response += (
            "Python is one of the most versatile languages in industry today. Here is a step-by-step master plan:\n\n"
            "**1. Strengthen the Core Fundamentals**\n"
            "- Master data structures: Lists, Tuples, Dictionaries, Sets, and List Comprehensions.\n"
            "- Understand Object-Oriented Programming (OOP): Classes, inheritance, `__init__`, and dunder methods.\n"
            "- Exception handling (`try-except-finally`), file I/O, and virtual environments (`venv`).\n\n"
            "**2. Advance to Practical Libraries**\n"
            "- **For Data & AI**: Dive into `numpy` (vectorized math), `pandas` (tabular data manipulation), and `matplotlib`/`seaborn`.\n"
            "- **For Web & APIs**: Learn `Flask` or `FastAPI` for lightweight RESTful web services.\n"
            "- **For Automation**: Use `requests` and `BeautifulSoup` for web scraping.\n\n"
            "**3. Daily Practice & Clean Code**\n"
            "- Solve Python challenges on LeetCode or HackerRank to write clean, idiomatic code.\n"
            "- Follow PEP 8 style guidelines and use type hints (`def greet(name: str) -> str:`).\n"
        )
    elif skill_lower in ["sql", "database"]:
        response += (
            "SQL is required in almost every software, data, and analytics role. Follow this roadmap:\n\n"
            "**1. Fundamental Querying**\n"
            "- Practice filtering and sorting: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `LIKE`.\n"
            "- Master aggregations: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, paired with `GROUP BY` and `HAVING`.\n\n"
            "**2. Relational Joins & Subqueries**\n"
            "- Understand the difference between `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, and `FULL OUTER JOIN`.\n"
            "- Practice nested queries and Common Table Expressions (`WITH cte AS (...)`).\n\n"
            "**3. Advanced Window Functions & Indexing**\n"
            "- Learn window functions: `ROW_NUMBER() OVER(PARTITION BY ...)`, `RANK()`, `LEAD()`, `LAG()`.\n"
            "- Understand database indexes, primary vs foreign keys, and query execution plans (`EXPLAIN`).\n"
        )
    elif skill_lower in ["react", "react.js", "reactjs"]:
        response += (
            "React is the industry standard for modern web interfaces. Here is how to level up:\n\n"
            "**1. Core React Hooks**\n"
            "- Master `useState` for UI state and `useEffect` for side-effects and API fetching.\n"
            "- Understand dependency arrays in `useEffect` to avoid infinite loops and memory leaks.\n"
            "- Learn `useRef` (DOM access), `useMemo`, and `useCallback` for performance optimization.\n\n"
            "**2. State Management & Routing**\n"
            "- Use React Router DOM for multi-page client-side routing.\n"
            "- Use React Context API for global state (like user auth or theme mode).\n\n"
            "**3. Real-World Component Design**\n"
            "- Build reusable UI components (modals, dropdowns, cards, toast notifications).\n"
            "- Handle loading skeletons, empty states, and API error toasts gracefully.\n"
        )
    elif skill_lower in ["machine learning", "ml"]:
        response += (
            "Machine Learning requires both mathematical intuition and practical coding. Here is your roadmap:\n\n"
            "**1. Intuition Over Equations**\n"
            "- Learn how algorithms work conceptually: Linear/Logistic Regression, Decision Trees, Random Forests, K-Means.\n"
            "- Understand overfitting vs underfitting and the bias-variance tradeoff.\n\n"
            "**2. Hands-on with Scikit-learn**\n"
            "- Build data preprocessing pipelines: imputation, one-hot encoding, feature scaling (`StandardScaler`).\n"
            "- Cross-validation (`KFold`), hyperparameter tuning (`GridSearchCV`), and evaluation metrics (Precision, Recall, ROC-AUC).\n\n"
            "**3. Work on Real Kaggle Datasets**\n"
            "- Don't just use clean tutorial datasets; practice handling missing data and outliers on real Kaggle competitions.\n"
        )
    else:
        response += (
            f"Here is a proven 3-step approach to master **{skill_name.capitalize()}**:\n\n"
            f"**1. Build a Solid Foundation**: Spend 1–2 weeks reading official documentation or watching a beginner crash course.\n"
            f"**2. Hands-on Project Practice**: Never learn in a vacuum—build a small, functioning project that uses {skill_name.capitalize()} within 48 hours of learning the syntax.\n"
            f"**3. Code Review & Documentation**: Upload your code to GitHub with a clean README explaining what it does, how to run it, and what you learned.\n"
        )

    if courses:
        response += "\n**🎓 Recommended Free Courses & Tutorials from Our Database:**\n"
        for c in courses[:3]:
            title = c.get("title", "")
            platform = c.get("platform", "")
            url = c.get("url", "#")
            desc = c.get("description", "")
            response += f"- **[{title}]({url})** ({platform}) – {desc}\n"
    
    return response


def _get_contextual_advice(user_context: dict) -> str:
    """Generate advice based strictly on user's real profile, skills, and test data."""
    career_goal = user_context.get("career_goal")
    current_skills = user_context.get("current_skills", [])
    strong_skills = user_context.get("strong_skills", [])
    weak_skills = user_context.get("weak_skills", [])
    missing_skills = user_context.get("missing_skills", [])
    readiness_score = user_context.get("readiness_score")
    test_score = user_context.get("test_score")
    test_total = user_context.get("test_total")

    if not career_goal and not current_skills:
        return (
            "### 📋 Your Profile Status\n\n"
            "I noticed you haven't set up your career goal or uploaded your resume yet.\n\n"
            "**To get the most personalized advice:**\n"
            "1. Go to **Profile** and set your target job role.\n"
            "2. Head to **Resume & Skills** to upload your resume and extract your technical skills.\n"
            "3. Take the short **Skill Assessment Test** to measure your strengths and weaknesses!\n\n"
            "Once you do that, I can give you a customized plan highlighting your exact skill gaps."
        )

    parts = [f"### 📊 Personalized Career Guidance for **{career_goal or 'Your Career'}**\n"]
    
    if readiness_score is not None:
        parts.append(f"- **Current Readiness Score**: **{readiness_score}%**")
    if test_total and test_total > 0:
        parts.append(f"- **Assessment Performance**: **{test_score}/{test_total}** questions answered correctly")
    
    parts.append("\n**Skill Breakdown from Your Analysis:**")
    
    if strong_skills:
        parts.append(f"- ✅ **Strong Skills ({len(strong_skills)})**: {', '.join(strong_skills)} — *Great foundation! Showcase these on your resume.*")
    
    if weak_skills:
        parts.append(f"- ⚠️ **Skills to Strengthen ({len(weak_skills)})**: {', '.join(weak_skills)} — *Found in your resume, but you can improve your confidence with quick practice.*")
        
    if missing_skills:
        parts.append(f"- ❌ **Missing Skills for {career_goal} ({len(missing_skills)})**: {', '.join(missing_skills[:6])} — *These are required by industry job postings for this role.*")
    
    parts.append("\n**🎯 What You Should Focus on Next:**")
    if missing_skills:
        top_focus = missing_skills[0]
        parts.append(f"1. **Priority #1**: Start learning **{top_focus}**. Check the **Courses** page for curated tutorials.")
    if weak_skills:
        parts.append(f"2. **Priority #2**: Review fundamentals for **{weak_skills[0]}**.")
    parts.append("3. **Priority #3**: Build a portfolio project that combines your strong skills with one newly learned skill.")

    return "\n".join(parts)


def generate_career_advice(user_message: str, user_context: dict) -> dict:
    """
    Main entry point for generating career assistant replies.
    Matches queries against student career topics, role roadmaps,
    skill improvements, project ideas, and interview prep.
    Returns: { "reply": str, "suggested_followups": list, "context_used": dict }
    """
    msg = user_message.strip()
    msg_lower = msg.lower()

    reply = ""
    suggested_followups = []
    matched_role = None

    # Check if a specific job role is mentioned
    for role_name in JOB_ROLES.keys():
        if role_name.lower() in msg_lower:
            matched_role = role_name
            break

    # ── Category 1: User's Profile / Gaps / "My status" ───────────────────────
    if any(k in msg_lower for k in ["my skill", "my gap", "my profile", "my status", "what should i focus", "what should i learn next", "how ready am i", "based on my"]):
        reply = _get_contextual_advice(user_context)
        suggested_followups = [
            "Which projects should I add to my resume?",
            "How can I prepare for technical interviews?",
            "How can I improve my Python skills?"
        ]

    # ── Category 2: Roadmap Requests ──────────────────────────────────────────
    elif "roadmap" in msg_lower or "learning path" in msg_lower or "how to become" in msg_lower:
        target_role_key = None
        if matched_role:
            target_role_key = matched_role.lower()
        elif user_context.get("career_goal") and user_context.get("career_goal").lower() in ROADMAPS:
            target_role_key = user_context.get("career_goal").lower()
        else:
            # Check keywords
            for r in ROADMAPS.keys():
                if r in msg_lower:
                    target_role_key = r
                    break

        if target_role_key and target_role_key in ROADMAPS:
            reply = ROADMAPS[target_role_key]
            suggested_followups = [
                f"Which projects should I add to my resume for {target_role_key.title()}?",
                "What skills do I need to become a Data Analyst?",
                "How can I prepare for technical interviews?"
            ]
        else:
            # Generic roadmap guidance
            reply = (
                "### 🗺️ General Engineering & Tech Career Roadmap\n\n"
                "To build a successful technical career, structure your journey in 4 distinct phases:\n\n"
                "1. **Core Language & Problem Solving (Months 1–2)**: Pick one language (Python, JavaScript, or Java) and solve basic algorithms.\n"
                "2. **Frameworks & Practical Tools (Months 3–4)**: Learn the standard web or data frameworks (React, Flask, Pandas, SQL).\n"
                "3. **Capstone Projects (Months 5–6)**: Build 2 distinct full-stack or data applications and deploy them publicly.\n"
                "4. **Interview Prep & Networking (Month 7+)**: LeetCode, resume tailoring, and mock technical interviews.\n\n"
                "💡 *Tip: Ask me for a specific roadmap, such as:* `Create a beginner-friendly roadmap for a Machine Learning Engineer` *or* `Data Analyst roadmap`."
            )
            suggested_followups = [
                "Create a beginner-friendly roadmap for a Machine Learning Engineer.",
                "What skills do I need to become a Data Analyst?",
                "Which projects should I add to my resume?"
            ]

    # ── Category 3: Role Skills Requirements ("What skills do I need to become...")
    elif any(k in msg_lower for k in ["what skills", "skills do i need", "skills required", "requirements for", "skills for"]):
        target_role = matched_role or user_context.get("career_goal") or "Data Analyst"
        
        # Check if matched role is in our database
        skills = JOB_ROLES.get(target_role)
        if not skills:
            # Fallback search
            for role_name, r_skills in JOB_ROLES.items():
                if any(w in msg_lower for w in role_name.lower().split()):
                    target_role = role_name
                    skills = r_skills
                    break

        if skills:
            reply = (
                f"### 🎯 Required Skills for a **{target_role}**\n\n"
                f"Based on real industry job postings, here are the essential technical skills:\n\n"
            )
            # Group into core vs secondary
            core_skills = skills[:len(skills)//2 + 1]
            advanced_skills = skills[len(skills)//2 + 1:]
            
            reply += "**Primary Must-Have Skills:**\n"
            for s in core_skills:
                reply += f"- **{s}**: Foundational requirement for standard entry-level responsibilities.\n"
            
            if advanced_skills:
                reply += "\n**Recommended Tools & Frameworks:**\n"
                for s in advanced_skills:
                    reply += f"- **{s}**: Gives you an edge in competitive applicant pools.\n"

            reply += (
                f"\n💡 *Want to test your proficiency? Take the Skill Assessment in the sidebar to see how many of these you already have!*"
            )
            suggested_followups = [
                f"Create a beginner-friendly roadmap for a {target_role}.",
                f"Which projects should I add to my resume for {target_role}?",
                "How can I prepare for technical interviews?"
            ]
        else:
            reply = (
                "Here are the most in-demand technical roles and their primary skill sets:\n"
                "- **Data Analyst**: Excel, SQL, Python, Pandas, Power BI / Tableau.\n"
                "- **Machine Learning Engineer**: Python, NumPy, Pandas, Scikit-learn, PyTorch/TensorFlow, Git, Docker.\n"
                "- **Full Stack Developer**: HTML/CSS, JavaScript, React, Node.js or Flask, SQL, Git.\n"
                "- **Cloud Engineer**: Linux, AWS, Docker, Kubernetes, Python, CI/CD.\n\n"
                "Which role would you like a detailed breakdown for?"
            )
            suggested_followups = [
                "What skills do I need to become a Data Analyst?",
                "Create a beginner-friendly roadmap for a Machine Learning Engineer.",
                "How can I improve my Python skills?"
            ]

    # ── Category 4: Skill Improvement ("How can I improve my...") ─────────────
    elif any(k in msg_lower for k in ["how can i improve", "how to improve", "learn python", "learn sql", "learn react", "master python", "improve my"]):
        # Identify which skill
        target_skill = "Python"
        for s in ["python", "sql", "react", "machine learning", "javascript", "excel", "pandas", "docker", "git", "html", "css", "c++", "java"]:
            if s in msg_lower:
                target_skill = s
                break
        
        reply = _format_skill_advice(target_skill)
        suggested_followups = [
            f"Which projects should I add to my resume using {target_skill.title()}?",
            "What skills do I need to become a Data Analyst?",
            "How can I prepare for technical interviews?"
        ]

    # ── Category 5: Resume & Projects ("Which projects should I add...") ───────
    elif any(k in msg_lower for k in ["project", "projects", "resume projects", "portfolio"]):
        target_role = matched_role or user_context.get("career_goal") or "Data Analyst"
        role_key = target_role.lower()

        # Find best matching project ideas
        selected_projects = PROJECT_IDEAS.get(role_key)
        if not selected_projects:
            for k in PROJECT_IDEAS.keys():
                if k in role_key:
                    selected_projects = PROJECT_IDEAS[k]
                    break
        if not selected_projects:
            selected_projects = PROJECT_IDEAS["data analyst"]

        reply = (
            f"### 📂 High-Impact Resume Projects for **{target_role}**\n\n"
            f"Recruiters look for projects that demonstrate real problem solving, clean code, and working demos rather than copy-pasted tutorial code:\n\n"
        )
        for i, p in enumerate(selected_projects, 1):
            reply += f"{i}. {p}\n\n"

        reply += (
            "**⭐ Top 3 Resume Tips for Technical Projects:**\n"
            "- **Quantify results**: Write *'Optimized model inference time by 28%'* instead of *'Made model fast'*.\n"
            "- **Include links**: Always link the GitHub repo AND a live demo (Render, Vercel, Streamlit, or YouTube demo).\n"
            "- **Clean README**: Include a project overview, screenshots/GIFs, architecture diagram, and simple setup instructions."
        )
        suggested_followups = [
            "How can I prepare for technical interviews?",
            "What skills do I need to become a Data Analyst?",
            "How can I improve my Python skills?"
        ]

    # ── Category 6: Technical Interview Preparation ───────────────────────────
    elif any(k in msg_lower for k in ["interview", "interview prep", "prepare for interview", "technical interview", "coding round"]):
        reply = INTERVIEW_GUIDE
        suggested_followups = [
            "Which projects should I add to my resume?",
            "How can I improve my Python skills?",
            "Create a beginner-friendly roadmap for a Machine Learning Engineer."
        ]

    # ── Category 7: General / Welcome / Fallback ──────────────────────────────
    else:
        user_name = user_context.get("user_name", "Student")
        career_goal = user_context.get("career_goal", "your chosen career")
        reply = (
            f"Hello {user_name}! 👋 I am your **SkillGap AI Career Assistant**.\n\n"
            f"I can help you build skills, plan your roadmap, build resume projects, and prepare for job interviews.\n\n"
            f"**Here are popular questions you can ask me right now:**\n"
            f"1. *What skills do I need to become a Data Analyst?*\n"
            f"2. *How can I improve my Python skills?*\n"
            f"3. *Create a beginner-friendly roadmap for a Machine Learning Engineer.*\n"
            f"4. *Which projects should I add to my resume?*\n"
            f"5. *How can I prepare for technical interviews?*\n"
            f"6. *What should I focus on next based on my profile?*\n\n"
            f"Feel free to click any suggestion below or type your question!"
        )
        suggested_followups = [
            "What skills do I need to become a Data Analyst?",
            "How can I improve my Python skills?",
            "Create a beginner-friendly roadmap for a Machine Learning Engineer.",
            "Which projects should I add to my resume?",
            "How can I prepare for technical interviews?"
        ]

    return {
        "reply": reply,
        "suggested_followups": suggested_followups,
        "context_used": {
            "career_goal": user_context.get("career_goal"),
            "readiness_score": user_context.get("readiness_score"),
            "skills_count": len(user_context.get("current_skills", [])),
        }
    }
