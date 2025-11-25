from flask import Flask, render_template, request, send_file, redirect, url_for
import generator
import outil_web
import tempfile
import os
import json
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "lettrix_secret_key"

# ----------------------------
# 🔒 CONFIG LIMITES EXPORTATION
# ----------------------------
LIMIT_FILE = "export_limits.json"
EXPORT_LIMIT = 2   # 2 exports par jour


def load_limits():
    if not os.path.exists(LIMIT_FILE):
        return {}
    with open(LIMIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_limits(data):
    with open(LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def can_export(ip):
    """Retourne (bool, remaining)"""
    data = load_limits()
    today = datetime.now().strftime("%Y-%m-%d")

    if ip not in data:
        data[ip] = {"date": today, "count": 0}
        save_limits(data)
        return True, EXPORT_LIMIT

    if data[ip]["date"] != today:
        data[ip] = {"date": today, "count": 0}
        save_limits(data)
        return True, EXPORT_LIMIT

    remaining = EXPORT_LIMIT - data[ip]["count"]
    return remaining > 0, remaining


def add_export(ip):
    data = load_limits()
    today = datetime.now().strftime("%Y-%m-%d")

    if ip not in data:
        data[ip] = {"date": today, "count": 0}

    if data[ip]["date"] != today:
        data[ip] = {"date": today, "count": 0}

    data[ip]["count"] += 1
    save_limits(data)


# ----------------------------
# 🖥️ ROUTES PRINCIPALES
# ----------------------------

@app.route("/", methods=["GET"])
def index():
    ip = request.remote_addr
    ok, remaining = can_export(ip)
    return render_template("index.html", lettre=None, remaining=remaining, can_export=ok)


@app.route("/generer", methods=["POST"])
def generer():
    return generer_base(page="index")


@app.route("/preview", methods=["POST"])
def preview():
    return generer_base(page="preview")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")

@app.route("/google70150802f6baa8d4.html")
def google_verification():
    return send_from_directory("static/verification", "google70150802f6baa8d4.html")



def generer_base(page="index"):
    champs = {
        "nom": request.form.get("nom"),
        "destinataire": request.form.get("destinataire"),
        "nom_entreprise": request.form.get("nom_entreprise"),
        "domaine": request.form.get("domaine"),
        "objet": request.form.get("objet"),
        "genre": request.form.get("genre"),
        "exp_adresse": request.form.get("exp_adresse"),
        "exp_cp": request.form.get("exp_cp"),
        "exp_ville": request.form.get("exp_ville"),
        "exp_email": request.form.get("exp_email"),
        "exp_tel": request.form.get("exp_tel"),
        "dest_adresse": request.form.get("dest_adresse"),
        "dest_cp": request.form.get("dest_cp"),
        "dest_ville": request.form.get("dest_ville"),
        "signature": request.form.get("signature")
    }

    categorie = request.form.get("categorie") or ""
    style = request.form.get("style") or ""

    for k in champs:
        champs[k] = champs[k] or ""

    texte = generator.generer_lettre(categorie=categorie, style=style, champs=champs)

    parts = [p.strip() for p in texte.split("\n\n") if p.strip()]
    intro = parts[0] if len(parts) >= 1 else ""
    conc = parts[-1] if len(parts) >= 2 else ""
    corps = "\n\n".join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")

    lettre = {
        **champs,
        "categorie": categorie,
        "style": style,
        "introduction": intro,
        "corps": corps,
        "conclusion": conc,
        "texte": texte
    }

    ip = request.remote_addr
    ok, remaining = can_export(ip)

    if page == "preview":
        return render_template("preview.html", lettre=lettre, remaining=remaining, can_export=ok)
    else:
        return render_template("index.html", lettre=lettre, remaining=remaining, can_export=ok)


# ----------------------------
# 📄 EXPORT WORD
# ----------------------------
@app.route("/export/word", methods=["POST"])
def export_word():
    ip = request.remote_addr
    ok, remaining = can_export(ip)
    if not ok:
        return redirect(url_for("index"))

    add_export(ip)
    lettre = dict(request.form)
    fichier = outil_web.generer_word_temp(lettre)
    return send_file(fichier, as_attachment=True, download_name="lettre.docx")


# ----------------------------
# 📄 EXPORT PDF
# ----------------------------
@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    ip = request.remote_addr
    ok, remaining = can_export(ip)
    if not ok:
        return redirect(url_for("index"))

    add_export(ip)
    lettre = dict(request.form)
    fichier = outil_web.generer_pdf_temp(lettre)
    return send_file(fichier, as_attachment=True, download_name="lettre.pdf")




if __name__ == "__main__":
    app.run(debug=True)
