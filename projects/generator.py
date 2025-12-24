import random, os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
LETTERS_DIR = os.path.join(BASE_DIR, "lettres", "resignation_letter", "english")

def load_variants(name):
    path = os.path.join(LETTERS_DIR, name)
    if not os.path.exists(path):
        return []
    return [p.strip() for p in open(path, encoding="utf-8").read().split("\n---\n") if p.strip()]

class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def pretty_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%B %d, %Y")
    except:
        return s

def generate_text(data):
    intros = load_variants("intro.txts")
    bodies = load_variants("body.txts")
    conclusions = load_variants("conclusion.txts")

    if not intros:
        intros = ["Please accept this letter as formal notice of my resignation from my position as {current_job_title} at {company_name}."]

    if not bodies:
        bodies = ["My resignation will be effective on {last_working_day}. {reason_for_resignation}"]

    if not conclusions:
        conclusions = ["Thank you for the opportunity to work at {company_name}. {transition_help}"]

    info = data.copy()
    info["letter_date"] = pretty_date(info.get("letter_date",""))
    info["last_working_day"] = pretty_date(info.get("last_working_day",""))

    intro = random.choice(intros).format_map(SafeDict(info))
    body = random.choice(bodies).format_map(SafeDict(info))
    concl = random.choice(conclusions).format_map(SafeDict(info))

    full_text = f"{intro}\n\n{body}\n\n{concl}\n\nSincerely,\n{info.get('employee_full_name','')}"
    return {"full_text": full_text}
