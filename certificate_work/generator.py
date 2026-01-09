import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
# Chemin corrigé pour ta structure : lettres/work_certificate/english
LETTERS_DIR = os.path.join(BASE_DIR, "lettres", "work_certificate", "english")

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
    # load variants
    intros = load_variants("intro.txts")
    bodies = load_variants("body.txts")
    conclusions = load_variants("conclusion.txts")

    # fallback variants
    if not intros:
        intros = ["This is to certify that {employee_name} worked as {position} at {company_name}."]
    if not bodies:
        bodies = ["Between {start_date} and {end_date}, {employee_name} demonstrated professionalism and fulfilled duties as described: {work_summary}"]
    if not conclusions:
        conclusions = ["We wish {employee_name} every success in their future endeavors."]

    # pick random parts
    intro = pick_random(intros)
    body = pick_random(bodies)
    conclusion = pick_random(conclusions)

    info = user_info.copy()
    # keep compatibility with both employer_name and company_name
    if not info.get("company_name") and info.get("employer_name"):
        info["company_name"] = info.get("employer_name")
    if not info.get("employer_name") and info.get("company_name"):
        info["employer_name"] = info.get("company_name")

    # format dates
    if info.get("start_date"):
        info["start_date"] = pretty_date(info["start_date"])
    if info.get("end_date"):
        info["end_date"] = pretty_date(info["end_date"])
    if info.get("signature_date"):
        info["signature_date"] = pretty_date(info["signature_date"])

    # safe formatting
    final_intro = intro.format_map(SafeDict(info))
    final_body = body.format_map(SafeDict(info))
    final_conclusion = conclusion.format_map(SafeDict(info))

    # build professional assembly with optional sections
    parts = []
    parts.append(final_intro)
    parts.append("")  # blank line

    # add work summary if provided (else use final_body)
    if info.get("work_summary"):
        parts.append(final_body)
    else:
        # if generator body didn't rely on work_summary, still include it
        parts.append(final_body)

    # optional skills / behaviour
    if info.get("skills"):
        parts.append("")
        parts.append("Key skills & competencies: " + info.get("skills"))
    if info.get("behaviour"):
        parts.append("")
        parts.append("Professional conduct: " + info.get("behaviour"))

    parts.append("")
    parts.append(final_conclusion)

    # final statement if provided
    if info.get("final_statement"):
        parts.append("")
        parts.append(info.get("final_statement"))

    # signature block hint (kept in generated text, actual signature placed in PDF)
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
