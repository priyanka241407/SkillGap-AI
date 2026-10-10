"""
Skill extraction service.
Reads the resume text, normalizes it, and matches against our skills database.
Uses simple keyword/regex matching - easy to understand for students.
"""

import re
import os
import csv

# Path to the data directory (one level up from backend)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")


def load_skills_db():
    """
    Load the skills database from skills.csv.
    Returns a dict: { canonical_name: [alias1, alias2, ...] }
    """
    skills_db = {}
    skills_csv = os.path.join(DATA_DIR, "skills.csv")
    with open(skills_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skill = row["skill"].strip()
            aliases = [a.strip().lower() for a in row["aliases"].split(",")]
            # Also add the skill name itself as an alias
            aliases.append(skill.lower())
            skills_db[skill] = aliases
    return skills_db


def extract_skills_from_text(text: str) -> list:
    """
    Given a block of text (from resume), identify which skills are present.

    Strategy:
    1. Lowercase the text
    2. For each skill in our database, check if the skill name or any alias appears in the text
    3. Use word boundary matching to avoid partial matches (e.g. "C" matching "CSS")
    4. Return a list of canonical skill names
    """
    if not text:
        return []

    text_lower = text.lower()
    skills_db = load_skills_db()
    found_skills = set()

    for canonical_skill, aliases in skills_db.items():
        for alias in aliases:
            # Use word boundary regex for reliable matching
            # \b matches at word boundaries
            # re.escape handles special chars like C++ or .js
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.add(canonical_skill)
                break  # No need to check more aliases for this skill

    return sorted(list(found_skills))


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""


def process_resume(file_path: str) -> dict:
    """
    Main function: given a resume file path, extract text and identify skills.
    Returns a dict with 'raw_text' and 'skills'.
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif file_ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    else:
        raw_text = ""

    skills = extract_skills_from_text(raw_text)

    return {
        "raw_text": raw_text[:2000],  # Keep only first 2000 chars for storage
        "skills": skills
    }
