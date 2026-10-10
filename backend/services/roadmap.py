"""
Roadmap generator service.
Builds a step-by-step learning roadmap based on the skill gap analysis.
"""


def generate_roadmap(
    career_goal: str,
    current_skills: list,
    strong_skills: list,
    weak_skills: list,
    missing_skills: list,
    required_skills: list,
) -> list:
    """
    Generate an ordered list of learning steps.

    Order:
    1. Skills already mastered (mark as 'done') - shown for confidence
    2. Weak skills (need improvement)
    3. Missing skills (sorted by priority)

    Each step contains enough info to display in the roadmap UI.
    """
    steps = []
    step_num = 1

    # Estimated time map (rough estimates for display purposes)
    time_estimates = {
        "Python": "3-4 weeks",
        "Pandas": "2 weeks",
        "NumPy": "1 week",
        "Matplotlib": "1 week",
        "Machine Learning": "6-8 weeks",
        "Deep Learning": "6-8 weeks",
        "Scikit-learn": "3 weeks",
        "TensorFlow": "4 weeks",
        "PyTorch": "4 weeks",
        "Statistics": "3-4 weeks",
        "SQL": "2-3 weeks",
        "HTML": "2 weeks",
        "CSS": "2 weeks",
        "JavaScript": "4 weeks",
        "React": "4-6 weeks",
        "Node.js": "3-4 weeks",
        "MongoDB": "2 weeks",
        "Git": "1 week",
        "Excel": "1-2 weeks",
        "Power BI": "2-3 weeks",
        "Data Visualization": "2 weeks",
        "NLP": "4-6 weeks",
        "Docker": "2-3 weeks",
    }
    default_time = "2-3 weeks"

    # Step 1: Strong skills (already know)
    for skill in strong_skills:
        steps.append({
            "step": step_num,
            "skill": skill,
            "status": "completed",
            "status_label": "✓ Already Know",
            "priority": "none",
            "estimated_time": time_estimates.get(skill, default_time),
            "description": f"You already have {skill} skills. Keep practicing to stay sharp.",
        })
        step_num += 1

    # Step 2: Weak skills (in resume but need improvement)
    for skill in weak_skills:
        steps.append({
            "step": step_num,
            "skill": skill,
            "status": "in_progress",
            "status_label": "↑ Improve",
            "priority": "High",
            "estimated_time": time_estimates.get(skill, default_time),
            "description": f"You have basic {skill} skills but need to improve. Focus on practice problems.",
        })
        step_num += 1

    # Step 3: Missing skills (sorted by priority)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_missing = sorted(
        missing_skills,
        key=lambda x: priority_order.get(x.get("priority", "Low") if isinstance(x, dict) else "Low", 2)
    )

    for item in sorted_missing:
        skill = item["skill"] if isinstance(item, dict) else item
        priority = item.get("priority", "Medium") if isinstance(item, dict) else "Medium"
        steps.append({
            "step": step_num,
            "skill": skill,
            "status": "not_started",
            "status_label": "→ Start Learning",
            "priority": priority,
            "estimated_time": time_estimates.get(skill, default_time),
            "description": f"{skill} is required for {career_goal}. Start from the basics.",
        })
        step_num += 1

    # Final step: Projects (always added at the end)
    steps.append({
        "step": step_num,
        "skill": "Projects",
        "status": "not_started",
        "status_label": "→ Build Projects",
        "priority": "High",
        "estimated_time": "Ongoing",
        "description": f"Build real projects to demonstrate your {career_goal} skills to employers.",
    })

    return steps
