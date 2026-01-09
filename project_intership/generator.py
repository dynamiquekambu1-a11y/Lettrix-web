import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
LETTERS_DIR = os.path.join(BASE_DIR, "lettres", "internship_application", "english")

def load_variants(filename):
    path = os.path.join(LETTERS_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [p.strip() for p in f.read().split("\n---\n") if p.strip()]

class SafeDict(dict):
    def __missing__(self, key):
        return ""

def pretty_date(s):
    if not s:
        return datetime.now().strftime("%B %d, %Y")
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%B %d, %Y")
    except:
        return s

def generate_text(info):
    info["date"] = pretty_date(info.get("date"))

    intro = load_variants("intro.txts") or [
        "I am writing to apply for the {internship_position} internship position at {company_name}."
    ]

    body = load_variants("body.txts") or [
        "I am currently a {current_level} student in {field_of_study} at {university}. "
        "I am highly motivated to gain practical experience through this internship.\n\n"
        "{motivation}\n\n"
        "My key skills include: {key_skills}.\n"
        "Relevant academic projects or experiences: {academic_projects}.\n"
        "I am available for an internship duration of: {internship_duration}."
    ]

    conclusion = load_variants("conclusion.txts") or [
        "I would be grateful for the opportunity to further discuss my application."
    ]

    full_text = "\n\n".join([
        random.choice(intro).format_map(SafeDict(info)),
        random.choice(body).format_map(SafeDict(info)),
        random.choice(conclusion).format_map(SafeDict(info)),
        "\nSincerely,\n" + info.get("applicant_name", "")
    ])

    return {"full_text": full_text}
