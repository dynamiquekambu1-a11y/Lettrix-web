import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
LETTERS_DIR = os.path.join(BASE_DIR, "lettres", "job_application", "english")

def load_variants(filename):
    path = os.path.join(LETTERS_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    return parts

class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def pretty_date(s):
    if not s:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%B %d, %Y")
        except:
            continue
    return s

def pick_random(variant_list):
    if not variant_list:
        return ""
    return random.choice(variant_list)

def generate_text(user_info):
    intros = load_variants("intro.txts")
    bodies = load_variants("body.txts")
    conclusions = load_variants("conclusion.txts")

    # fallback si fichiers vides
    if not intros:
        intros = [
            "Dear Hiring Manager, my name is {applicant_name}, applying for the position of {position_applied} at {company_name}."
        ]
    if not bodies:
        bodies = [
            "I have {experience_years} years of experience, strong skills such as {skills}, and achievements: {achievements}. {why_you_want}"
        ]
    if not conclusions:
        conclusions = [
            "I would be grateful for the opportunity to discuss my application further."
        ]

    intro = pick_random(intros)
    body = pick_random(bodies)
    conclusion = pick_random(conclusions)

    info = user_info.copy()

    # format signature date
    if info.get("signature_date"):
        info["signature_date"] = pretty_date(info["signature_date"])

    final_intro = intro.format_map(SafeDict(info))
    final_body = body.format_map(SafeDict(info))
    final_conclusion = conclusion.format_map(SafeDict(info))

    parts = [final_intro, "", final_body, "", final_conclusion]

    if info.get("cover_letter_text"):
        parts.append("")
        parts.append(info["cover_letter_text"])

    signer = info.get("signer_name", "")
    signer_role = info.get("signer_role", "")
    if signer or signer_role:
        parts.append("")
        parts.append(f"Sincerely,\n{signer}\n{signer_role}")

    full_text = "\n\n".join([p for p in parts if p is not None])

    return {
        "intro": final_intro,
        "body": final_body,
        "conclusion": final_conclusion,
        "full_text": full_text
    }
